def split_message(text: str, max_length: int) -> list[str]:
    """
    주어진 텍스트를 max_length 이내의 조각으로 나눕니다.
    """
    if not text:
        return []

    lines = text.split('\n')
    result = []
    current_chunk = []
    current_length = 0

    for line in lines:
        # 1. 한 줄 자체가 이미 max_length를 초과하는 경우 (강제 분할 필요)
        if len(line) > max_length:
            # 먼저 현재까지 쌓인 버퍼가 있다면 결과에 추가
            if current_chunk:
                result.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0

            # 긴 줄을 max_length 단위로 강제 슬라이싱
            temp_line = line
            while len(temp_line) > max_length:
                result.append(temp_line[:max_length])
                temp_line = temp_line[max_length:]

            # 남은 부분은 다음 처리를 위해 current_chunk에 보관
            if temp_line:
                current_chunk.append(temp_line)
                current_length = len(temp_line)

        else:
            # 2. 줄바꿈을 포함했을 때 max_length를 초과하는지 계산
            # (current_length + 줄바꿈(1) + 새 라인 길이)
            added_length = current_length + (1 if current_length > 0 else 0) + len(line)

            if added_length <= max_length:
                current_chunk.append(line)
                current_length = added_length
            else:
                # 초과하면 지금까지의 덩어리를 결과에 저장하고 새로 시작
                result.append("\n".join(current_chunk))
                current_chunk = [line]
                current_length = len(line)

    # 마지막으로 남은 버퍼 처리
    if current_chunk:
        result.append("\n".join(current_chunk))

    return result

# 이후 하단에 1단계에서 작성한 테스트 코드를 배치하여 실행하면 됩니다.
