from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools import compose_video



video_composer_agent = Agent(
    name="VideoComposerAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    description="",
    instruction="",
    output_key="video_composer_output",
    tools=[compose_video]
)
