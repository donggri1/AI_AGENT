import firebase_admin
from firebase_admin import credentials , firestore
from datetime import datetime

# cred = credentials.Certificate("path/to/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

class FirebaseDB:
    def __init__(self) :
        cred = credentials.Certificate(
            "agent-bddc9-firebase-adminsdk-fbsvc-4e5b5fd072.json"
            )
        firebase_admin.initialize_app(cred) # firebase 앱 초기화

        self.db = firestore.client()  # Firestore 클라이언트 초기화

        self.collection_name = "conversation_history"

    def save_conversation(self,user_message:str,bot_response:str):
        doc_data = {
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp":datetime.now()
        }
        self.db.collection(self.collection_name).add(doc_data)

    def get_conversation_context(self,limit:int=10):
        docs = list(self.db.collection(self.collection_name).order_by("timestamp",direction="ASCENDING").limit(limit).stream())
        # 최신 대화부터 limit 개수만큼 가져오기

        if not docs:
            return "이전 대화 없음"
        context = "=== 최근 대화 기록 ===\n"
        for i, chat in enumerate(docs,1):
            context += f"{i}, 사용자 : {chat.get('user_message')}\n"
            context += f"     봇 : {chat.get('bot_response')}\n"
        return context

db = FirebaseDB()

def add_to_conversation(user_message:str , bot_response:str):
    db.save_conversation(user_message, bot_response)

def get_conversation_context():
     return db.get_conversation_context()
