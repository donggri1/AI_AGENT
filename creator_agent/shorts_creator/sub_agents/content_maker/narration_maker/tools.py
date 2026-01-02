from google.genai import types
from openai import OpenAI
from google.adk.tools.tool_context import ToolContext
from typing import List, Dict , Any


# OpenAI 클라이언트 초기화
client = OpenAI()

# 사용할 TTS 모델 및 음성 설정
TTS_MODEL = "tts-1-hd"
TTS_VOICE = "nova"

AVG_WORDS_PER_SECOND = 2.5 # 한국어/영어 평균말하기 속도
NATURAL_SPEED_MIN = 0.9 # 자연스러운 최소 속도
NATURAL_SPEED_MAX = 1.2 # 자연스러운 최대 속도


async def generate_narration(
        tool_context: ToolContext, narration_requests: List[Dict[str, Any]]
)-> Dict[str, Any]:
    """
    OpenAI TTS API를 사용하여 각 장면에 대한 나레이션 오디오를 생성합니다.
    목표 지속시간에 맞춰 음성 속도를 조절하며 입력값에 대한 유효성 검사를 진행합니다.

    Args:
        tool_context: 아티팩트를 조회하고 저장하기 위한 ToolContext 객체.
        narration_requests: 각 장면에 대한 나레이션 생성 정보가 담긴 딕셔너리 리스트.
                          - 'scene_id' (str): 장면의 고유 식별자.
                          - 'narration_text' (str): 음성으로 변환할 텍스트.
                          - 'duration' (int or float): 나레이션의 목표 지속 시간 (초).

    Returns:
        생성된 모든 오디오 파일의 정보가 포함된 딕셔너리.
    """
    narration_results =[]

    existing_artifacts = await tool_context.list_artifacts()

    for request in narration_requests:
        scene_id = request["scene_id"]
        narration_text = str(request["narration_text"])

        output_filename = f"scene_{scene_id}_narration.mp3"

        if output_filename in existing_artifacts:
            narration_results.append({
                "scene_id": scene_id,
                "filename" : output_filename,
                "status" : "skipped_existing",
                "narration_text": narration_text,
            })
            continue
        try:

            # --- duration 값 안전하게 처리 ---
            target_duration = 0.0
            try:
                duration_val = request.get("duration", None)
                if duration_val is not None:
                    target_duration = float(duration_val)

            except (ValueError, TypeError):
                target_duration = 0.0

            #목표 지속시간(duration)에 맞춰 음성 속도(speed) 계산
            speed = 1.0 # 기본 속도
            word_count = len(narration_text.split())

            if target_duration > 0 and word_count >0:
                estimated_duration = word_count / AVG_WORDS_PER_SECOND
                calculated_speed = estimated_duration/target_duration
                speed = max(NATURAL_SPEED_MIN,min(NATURAL_SPEED_MAX,calculated_speed))

            response = client.audio.speech.create(
                model=TTS_MODEL,
                voice=TTS_VOICE,
                input=narration_text,
                speed= speed

            )
            audio_artifact = types.Part(
                inline_data=types.Blob(mime_type="audio/mpeg", data=response.content)
            )

            await tool_context.save_artifact(
                filename=output_filename,
                artifact=audio_artifact,
            )

            narration_results.append(
                {
                    "scene_id": scene_id,
                    "filename": output_filename,
                    "status": "generated",
                    "narration_text": narration_text,
                }
            )
        except Exception as e:
            error_msg = f"Failed to generate narration for scene {scene_id}: {str(e)}"
            narration_results.append(
                {
                    "scene_id": scene_id,
                    "filename": output_filename,
                    "status": "error",
                    "error_message": error_msg,
                }
            )
    return {
        "success": True ,
        "narrations" : narration_results
    }
