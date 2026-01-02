from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import DESCRIPTION,INSTRUCTION
from pydantic import BaseModel,Field
from .tools import generate_narration


narration_maker_agent = Agent(
    name="NarrationMakerAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        generate_narration
    ]
)
