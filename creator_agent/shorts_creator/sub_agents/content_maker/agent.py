import os

from google.adk.agents import Agent,ParallelAgent
from .image_maker.agent import image_maker_agent
from .narration_maker.agent import narration_maker_agent


content_maker_agent = ParallelAgent(
    name="ContentMakerAgent",
    description="""
    'content_planner_agent'가 생성한 기획안을 바탕으로 이미지와 나레이션 음성 파일을 제작하는 에이전트입니다.
    'content_planner_output'을 장면(scene)별로 처리하며, 각 장면에 대해 하나의 이미지와 하나의 나레이션을 생성합니다.
    예를 들어, 기획안에 5개의 장면이 있다면, 이 에이전트는 5개의 이미지와 5개의 나레이션 파일을 생성합니다.
    각 장면의 이미지와 나레이션 생성 작업은 효율성을 위해 병렬로 수행됩니다.
    """,
    sub_agents=[
        image_maker_agent,
        narration_maker_agent
    ]
)
