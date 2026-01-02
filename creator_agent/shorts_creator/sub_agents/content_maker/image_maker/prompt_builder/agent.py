from typing import List, Dict , Any
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel,Field
from .prompt import DESCRIPTION, INSTRUCTION


class OptPromptSchema(BaseModel):
    scene_id : int = Field(description="content_planner_output의 Scene ID")
    enhanced_prompt : str = Field(
        description="쇼츠 Scene 별 이미지 생성을 위한 prompt for image 및 text overlay 지침이 포함된 상세 prompt"
    )

class PromptBuilderSchema(BaseModel):
    opt_prompts : List[OptPromptSchema] = Field(
        description="쇼츠 Scene 별 최적화 된 이미지 생성 prompt 배열"
    )

prompt_builder_agent = Agent(
    name="PromptBuilderAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    output_schema=PromptBuilderSchema,
    output_key="prompt_builder_output",
)
