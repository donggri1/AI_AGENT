from google.adk.agents import Agent,SequentialAgent
from .prompt_builder.agent import prompt_builder_agent
from .image_builder.agent import image_builder_agent


image_maker_agent = SequentialAgent(
    name="ImageMakerAgent",
    sub_agents=[
        prompt_builder_agent,
        image_builder_agent
    ]
)
