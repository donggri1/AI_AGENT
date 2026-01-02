from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import DESCRIPTION, INSTRUCTION
from .tools import generate_images



image_builder_agent = Agent(
    name="ImageBuilderAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    output_key="image_builder_output",
    tools=[generate_images,]
)
