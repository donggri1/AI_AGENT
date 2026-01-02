import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
from env import OPENAI_API_KEY,REPLICATE_API_TOKEN
from shorts_creator.prompt import INSTRUCTION,DESCRIPTION
from .sub_agents.content_planner.agent import content_planner_agent
from .sub_agents.content_maker.agent import content_maker_agent
from .sub_agents.video_composer.agent import video_composer_agent




os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

root_agent = Agent(
    name = "ShortsCreatorAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        AgentTool(agent=content_planner_agent),
        AgentTool(agent=content_maker_agent),
        AgentTool(agent=video_composer_agent),
        ],
)

