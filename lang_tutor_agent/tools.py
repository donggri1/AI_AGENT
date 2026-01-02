"""
[Note]
Indexing (pre retrieval)
- 문서 ---(분할)---> chunk1, chunk2, ... ---(임베딩)---> 행렬데이터 ---(저장)---> 벡터DB

Retrieval (post retrieval)
- 사용자 질문 ---(임베딩)---> 행렬데이터 ---(검색)---> 벡터DB ---> chunk1, chunk2, ... ---> 답변생성

벡터 DB -> Pyncone(유료), Chroma(무료) 등등

청크(Chunk) = RAG에서 문서를 나눠 임베딩하는 “정보 단위”.
"""

import os
from typing import Type, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from env import OPENAI_API_KEY
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

PDF_FILENAME= os.path.join("knowledge","29ESLConversationTopic.pdf")
PERSIST_DIR = os.path.join(".chroma","esl_topics")


def _qa(question):

    os.makedirs(PERSIST_DIR, exist_ok=True)

    embeddings = OpenAIEmbeddings()

    try:
        has_index = bool(os.listdir(PERSIST_DIR))

    except Exception:
        has_index = False

    if has_index:
        # 기존 인덱스 로드

        vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)

    else :
        # 새로운 인덱스 생성
        loader = PyPDFLoader(PDF_FILENAME)
        docs = loader.load()

        #문서 -> chunk로 분할
        splitter = RecursiveCharacterTextSplitter( #pdf로 분할할꺼기 때문에 기본적인거 사용 ,이외에도 많음
            chunk_size=800, #문서를 너무 길게 넣으면 벡터 임베딩이 부정확해짐 ,너무 짧으면 문맥이 끊겨서 검색시 정보 손실이 발생
            chunk_overlap=200, # 인접
        )
        chunks = splitter.split_documents(docs)

        #임베딩
        vectordb = Chroma.from_documents(chunks,embeddings,persist_directory=PERSIST_DIR)

    retriever = vectordb.as_retriever(search_kwargs={"k":3}) # 리트리버 단계에서 검색할 청크 개수 ,사용자의 질문을 임베딩한 뒤 , 가장유사한 k개의 청크를 벡터db에서 검색한다
    llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)

    # chain_type란
    # LLM 이 검색된 여러개의 chunk를 어떻게 조합해서 최종 답변을 생성할지 결정하는 방식
    # stuff : 가장 간단한 방법. 모든 청크를 한 번에 LLM 에 전달하여 답변 생성 (청크의 수가 적을 때 유용)
    # map_reduce : 각 청크를 개별적으로 처리한 다음, 모든 개별 답변을 종합하여 최종 답변 생성 (청크의 수가 많을 때 유용)
    # refine : 첫 번째 청크로 답변을 생성하고, 이 답변과 다음 청크를 함께 LLM 에 전달하여 답변을 개선 (긴 문서를 처리하고, 보다 상세한 답변을 생성할 때 유용)
    # map_rerank : 각 청크에서 답변을 생성하고, 각 답변의 연관성 점수를 매긴 다음, 가장 높은 점수의 답변을 반환 (정확하고 간결한 답변을 원할 때 유용)

    return RetrievalQA.from_chain_type(llm=llm,chain_type="stuff",retriever=retriever).run(question)


class RAGToolInput(BaseModel):
    question : str = Field(...,description="ESL 주제 PDF를 사용해 답변할 질문")

class RAGTool(BaseTool):
    name: str = "ESL_Chroma_RAG"
    description: str =(
        "Retrieves from '29 ESL Conversation Topics' PDF via ChromaDB and answers questions."
    )
    args_schema: Type[BaseModel] = RAGToolInput

    def _run(self,question:str):
        try:
            return _qa(question)
        except Exception as e:
            return f"Chroma RAG 사용 중 오류 : {e}"


rag_tool = RAGTool()
