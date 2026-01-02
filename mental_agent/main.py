
from lina.agent import root_agent as lina_agent
from adk_chat import chat

ai_response =chat(agent=lina_agent,message="안녕 나는 이동찬이야.")

print(ai_response)
