from google.adk.agents import Agent,LoopAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext
from .prompt import CRITIC_DESCRIPTION,CRITIC_INSTRUCTION,PLANNER_DESCRIPTION,PLANNER_INSTRUCTION
from pydantic import BaseModel,Field



MODEL = LiteLlm(model="openai/gpt-4o")




class SceneSchema(BaseModel):

    id: int = Field(description="장면 id 번호")
    image_description: str = Field(description="생성할 이미지에 대한 상세 설명")
    narration: str = Field(description="장면에 대한 나레이션(텍스트)")
    text_overay: str = Field(description="이미지에 오버레이될 텍스트")
    text_overay_location: str = Field(
        description="이미지 위 텍스트 위치 (예: 'middle left', 'top center')"
    )
    duration: int = Field(description="해당 장면의 지속 시간(초)")


class PlanSchema(BaseModel):
    topic: str = Field(description="쇼츠 영상의 주제")
    scenes: list[SceneSchema] = Field(description="장면의 목록")
    total_duration: int = Field(description="총 영상 길이(초, 최대 25초)")


class CriticSchema(BaseModel):
    score: int = Field(description="기획안의 점수 (0-100)")
    feedback: str = Field(description="구체적이고 건설적인 피드백")

plan_generator_agent = Agent(
    name= "PlanGeneratorAgent",
    model=MODEL,
    description=PLANNER_DESCRIPTION,
    instruction=PLANNER_INSTRUCTION,
    output_schema=PlanSchema,
    output_key="content_planner_output",
)

async def plan_is_finalized(tool_context: ToolContext):
    # 최종 기획안이 확정되었을 때 이 도구를 호출해서 루프를 종료합니다.
    tool_context.actions.escalate = True # SubAgent 에서 상위 에이전트로 넘김
    return

plan_critic_agent = Agent(
    name= "PlanCriticAgent",
    model=MODEL,
    description=CRITIC_DESCRIPTION,
    instruction=CRITIC_INSTRUCTION,
    output_schema=CriticSchema,
    output_key="critic_output",
    tools=[plan_is_finalized]
)


content_planner_agent = LoopAgent(
    name="ContentPlannerAgent",
    max_iterations=3,
    description="Plans the overall content structure for YouTube shorts by generating and refining content plans through iterative review cycles.",
    sub_agents=[
        plan_generator_agent,
        plan_critic_agent
    ]
)
