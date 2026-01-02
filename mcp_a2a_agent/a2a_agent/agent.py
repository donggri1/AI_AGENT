from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.remote_a2a_agent import(
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH
)

lina_agent = RemoteA2aAgent(
    name="LinaAgent",
    description="친구같은 심리 상담가 Lina입니다.",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)


root_agent = Agent(
    name = "HelperAgent",
    description="상담 신청을 하면 최대한 문제를 해결해줍니다.",
    model=LiteLlm("openai/gpt-4o"),
    sub_agents=[
        lina_agent,
    ]
)
