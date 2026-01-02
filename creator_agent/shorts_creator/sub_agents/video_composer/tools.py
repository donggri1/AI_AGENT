import subprocess
import re
import tempfile
import os
from google.adk.tools.tool_context import ToolContext
import google.genai.types as types

# FFmpeg 다운로드: https://ffmpeg.org/download.html


def _parse_scene_index(artifact_filename: str) -> int:
    """아티팩트 파일명에서 씬 인덱스를 추출합니다

    Args:
        artifact_filename: scene_N_*.jpg 형식의 파일명

    Returns:
        추출된 씬 번호, 없으면 0
    """
    pattern_match = re.search(r"scene_(\d+)_", artifact_filename)
    return int(pattern_match.group(1)) if pattern_match else 0


def _categorize_artifacts(artifact_list: list[str]) -> tuple[list[str], list[str]]:
    """아티팩트 목록을 이미지와 오디오로 분류합니다

    Args:
        artifact_list: 전체 아티팩트 파일명 목록

    Returns:
        (이미지 파일명 리스트, 오디오 파일명 리스트) 튜플
    """
    visual_assets = []
    sound_assets = []

    for asset_name in artifact_list:
        if asset_name.startswith("scene_") and asset_name.endswith("_image.jpg"):
            visual_assets.append(asset_name)
        elif asset_name.startswith("scene_") and asset_name.endswith("_narration.mp3"):
            sound_assets.append(asset_name)

    # 씬 번호 순으로 정렬
    visual_assets.sort(key=_parse_scene_index)
    sound_assets.sort(key=_parse_scene_index)

    return visual_assets, sound_assets


def _construct_ffmpeg_filters(scene_metadata: list[dict]) -> list[str]:
    """FFmpeg 필터 그래프를 생성합니다

    Args:
        scene_metadata: 씬별 메타데이터 (duration 포함)

    Returns:
        FFmpeg filter_complex에 사용될 필터 문자열 리스트
    """
    filter_expressions = []
    scene_count = len(scene_metadata)

    # 각 씬별 비디오/오디오 스트림 생성
    for idx in range(scene_count):
        clip_duration = scene_metadata[idx].get("duration", 4)
        frame_count = int(30 * clip_duration)  # 30fps 기준 프레임 수

        # 비디오 필터: 이미지를 1080x1920 세로 영상으로 변환하고 반복
        video_filter = (
            f"[{idx * 2}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,"
            f"loop={frame_count - 1}:size=1:start=0[v{idx}]"
        )
        filter_expressions.append(video_filter)

        # 오디오 필터: 그대로 통과
        audio_filter = f"[{idx * 2 + 1}:a]anull[a{idx}]"
        filter_expressions.append(audio_filter)

    # 모든 비디오 스트림 연결
    concatenated_video_inputs = "".join(f"[v{i}]" for i in range(scene_count))
    filter_expressions.append(
        f"{concatenated_video_inputs}concat=n={scene_count}:v=1:a=0[outv]"
    )

    # 모든 오디오 스트림 연결
    concatenated_audio_inputs = "".join(f"[a{i}]" for i in range(scene_count))
    filter_expressions.append(
        f"{concatenated_audio_inputs}concat=n={scene_count}:v=0:a=1[outa]"
    )

    return filter_expressions


async def compose_video(tool_context: ToolContext) -> str:
    """이미지와 오디오 아티팩트로부터 최종 유튜브 쇼츠 영상을 조립합니다

    Args:
        tool_context: 상태 및 아티팩트 접근을 위한 도구 컨텍스트

    Returns:
        비디오 조립 프로세스에 대한 정보 문자열
    """
    cleanup_file_list = []  # 정리할 임시 파일 추적

    try:
        # 컨텍스트에서 콘텐츠 계획 읽기
        planner_result = tool_context.state.get("content_planner_output", {})
        scene_data = planner_result.get("scenes", [])

        if not scene_data:
            return "씬 데이터가 없습니다."

        # 사용 가능한 모든 아티팩트 조회
        available_artifacts = await tool_context.list_artifacts()

        # 이미지와 오디오 파일 분류 및 정렬
        visual_artifacts, sound_artifacts = _categorize_artifacts(available_artifacts)

        # 아티팩트 개수 검증
        expected_count = len(scene_data)
        if (
            len(visual_artifacts) != expected_count
            or len(sound_artifacts) != expected_count
        ):
            return f""""
                artifacts 부족: a total of {expected_count} images and audio files were expected,
                {len(visual_artifacts)}개의 images, {len(sound_artifacts)}개의 narration files
                """

        # 아티팩트 로드 및 임시 파일 생성
        stored_visual_paths = []
        stored_sound_paths = []

        for visual_name, sound_name in zip(visual_artifacts, sound_artifacts):
            # 이미지 아티팩트 로드 및 저장
            visual_artifact = await tool_context.load_artifact(filename=visual_name)
            if visual_artifact and visual_artifact.inline_data:
                visual_temp_file = tempfile.NamedTemporaryFile(
                    suffix=".jpg", delete=False
                )
                visual_temp_file.write(visual_artifact.inline_data.data)  # type:ignore
                visual_temp_file.close()
                stored_visual_paths.append(visual_temp_file.name)
                cleanup_file_list.append(visual_temp_file.name)
            else:
                return f"이미지 artifacts 로드 실패: {visual_name}"

            # 오디오 아티팩트 로드 및 저장
            sound_artifact = await tool_context.load_artifact(filename=sound_name)
            if sound_artifact and sound_artifact.inline_data:
                sound_temp_file = tempfile.NamedTemporaryFile(
                    suffix=".mp3", delete=False
                )
                sound_temp_file.write(sound_artifact.inline_data.data)  # type:ignore
                sound_temp_file.close()
                stored_sound_paths.append(sound_temp_file.name)
                cleanup_file_list.append(sound_temp_file.name)
            else:
                return f"나레이션 artifact 로드 실패: {sound_name}"

        # FFmpeg 입력 인자 구성
        ffmpeg_inputs = []
        for visual_path, sound_path in zip(stored_visual_paths, stored_sound_paths):
            ffmpeg_inputs.extend(["-i", visual_path, "-i", sound_path])

        # FFmpeg 필터 그래프 생성
        filter_graph = _construct_ffmpeg_filters(scene_data)

        # 최종 출력 파일 생성
        output_temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_temp_file.close()
        final_output_path = output_temp_file.name
        cleanup_file_list.append(final_output_path)

        # 최종 FFmpeg 명령어 조립
        encoding_command = (
            ["ffmpeg", "-y"]
            + ffmpeg_inputs
            + [
                "-filter_complex",
                ";".join(filter_graph),
                "-map",
                "[outv]",
                "-map",
                "[outa]",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-pix_fmt",
                "yuv420p",
                "-r",
                "30",
                final_output_path,
            ]
        )

        # FFmpeg 실행
        subprocess.run(encoding_command, capture_output=True, text=True, check=True)

        # 최종 비디오를 아티팩트로 저장
        with open(final_output_path, "rb") as video_file:
            encoded_video_data = video_file.read()

        video_artifact = types.Part(
            inline_data=types.Blob(mime_type="video/mp4", data=encoded_video_data)
        )

        await tool_context.save_artifact(filename="shorts.mp4", artifact=video_artifact)

        # 전체 영상 길이 계산
        complete_duration = sum(s.get("duration", 4) for s in scene_data)

        assembly_result = {
            "status": "success",
            "scenes_processed": len(scene_data),
            "total_duration": complete_duration,
            "output_file": "shorts.mp4",
            "resolution": "1080x1920",
            "format": "MP4 (H.264/AAC)",
        }

        return str(assembly_result)

    except subprocess.CalledProcessError as ffmpeg_error:
        error_details = {
            "status": "ffmpeg_error",
            "error": str(ffmpeg_error),
            "stderr": ffmpeg_error.stderr,
            "stdout": ffmpeg_error.stdout,
        }
        return str(error_details)

    except Exception as general_error:
        error_details = {"status": "error", "error": str(general_error)}
        return str(error_details)

    finally:
        # 임시 파일 정리
        for cleanup_target in cleanup_file_list:
            try:
                if os.path.exists(cleanup_target):
                    os.unlink(cleanup_target)
            except Exception as cleanup_error:
                print(f"error: {cleanup_error}")
