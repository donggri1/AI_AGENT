
import os
from crewai import Crew,Agent,Task,Process
from crewai.project import CrewBase,task,agent,crew
from tools import web_search_tool,naver_search_tool,google_search_tool
from env import GEMINI_API_KEY
from db import get_conversation_context

os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY


@CrewBase
class ChatBotCrew:

    def summary_agent(self) -> Agent:
        return Agent(
            role="대화 요약 전문가",
            goal="주어진 대화 내용을 간결하고 명확하게 요약한다.",
            backstory="""
            당신은 복잡한 대화 내용을 핵심 정보만을 추출하여 이해하기 쉽게 요약하는 데 탁월한 능력을 가진 전문가입니다.
            다양한 주제와 상황에 대한 대화를 빠르게 파악하고, 중요한 포인트를 놓치지 않으면서도 간결한 요약을 제공하는 것이 당신의 사명입니다.
            """,
            llm="gemini/gemini-2.5-flash",
            verbose=True,
        )
    def communication_agent(self) -> Agent:
            return Agent(
                role="전문 소통 분석가",
                goal="요약된 문맥과 검색된 정보를 바탕으로 사용자에게 최적의 답변을 제공한다.",
                backstory="""당신은 정보 분석가로서 요약된 과거 맥락을 이해하고,
                필요시 웹 검색을 통해 최신 정보를 결합하여 가장 친절하고 정확하게 답변합니다.""",
                llm="gemini/gemini-2.0-flash",
                verbose=True
            )

    @task
    def summary_task(self) -> Task:
        return Task(
            description=f"""
            아래의 DB 대화 기록을 읽고, 사용자의 새로운 메시지('{{message}}')와 연관된
            핵심 내용을 3문장 내외로 요약하세요.

            DB 대화 기록:
            {get_conversation_context()}
            """,
            expected_output="사용자의 의도와 과거 대화 맥락이 포함된 요약본.",
            agent=self.summary_agent()
        )

    @task
    def communication_task(self) -> Task:
        return Task(
            description="""
            사용자로부터 받은 메시지('{message}')를 단계별로 분석합니다.
            1. 질문의 핵심 키워드와 숨은 의도를 파악합니다.
            2. 필요 시, 웹 검색 도구를 사용하여 관련 최신 정보를 찾습니다.
            3. 수집된 정보를 종합하여 사용자가 이해하기 쉬운 형태로 명확하고 친절한 답변을 생성합니다.
            """,
            expected_output="""
            사용자의 질문 의도에 완벽하게 부합하는, 명확하고 간결하며 친절한 톤의 한국어 답변.
            질문이 정보성 질문의 경우, 핵심 내용을 요약하고 신뢰할 수 있는 출처(URL)를 포함해야 합니다.
            분석 과정이나 단계별 설명 없이, 최종 답변만 출력하세요.
            """,
            tools=[naver_search_tool,google_search_tool],
            agent = self.communication_agent()
            context=[self.summary_task()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.summary_agent(), self.communication_agent()],
            tasks=[self.summary_task(), self.communication_task()],
            process=Process.sequential, # 순차적으로 진행
            verbose=True,
        )

