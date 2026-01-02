from google.adk.sessions import InMemorySessionService,DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.agents import BaseAgent
from google.adk.models.lite_llm import LiteLlm
import asyncio


# 세션 초기화
# session_service = InMemorySessionService()
session_service = DatabaseSessionService(db_url="sqlite:///sessions.db")

# 세션 생성
async def async_chat(
    message:str ,
    agent : BaseAgent,
    user_id= "default_user" ,
    session_id="default_session",
    app_name="default_app",
    state={}

):

    result = ""
    await session_service.create_session(
        app_name=app_name,
        user_id=session_id,
        session_id=session_id,
    )

    # ADK Runner를 사용해서 agent랑 대화
    runner = Runner(
        app_name="default_app",
        agent= agent,
        session_service= session_service
    )
    event = runner.run_async(
        user_id=session_id,
        session_id=session_id,
        new_message=types.Content(
            parts=[types.Part(text=message)],
            role="user"
            )
    )



    async for ev in event:
        if ev.content and ev.content.role =="model" and ev.content.parts:
            for part in ev.content.parts:
                if part.text:
                    result += part.text
    return result

def chat(
    message:str ,
    agent : BaseAgent,
    user_id= "default_user" ,
    session_id="default_session",
    app_name="default_app",
    state={}
):
    return asyncio.run(async_chat(message,agent,user_id,session_id,app_name,state))

