"""
Dedup Engine — 텍스트 유사도 기반으로 중복/클립 영상을 판별합니다.

전략:
1. 짧은 영상의 텍스트가 긴 영상의 텍스트에 포함되는지 검사
2. SequenceMatcher로 유사도를 계산
3. 임계값(80%) 이상이면 중복으로 판정
"""
from difflib import SequenceMatcher
from config import SIMILARITY_THRESHOLD


def normalize_text(text):
    """텍스트를 비교 가능한 형태로 정규화합니다."""
    if not text:
        return ""
    # 소문자 변환, 연속 공백 제거
    return " ".join(text.lower().split())


def is_subset(short_text, long_text, threshold=SIMILARITY_THRESHOLD):
    """짧은 텍스트가 긴 텍스트의 부분집합인지 확인합니다.

    Sliding window 방식으로 긴 텍스트의 각 구간과 짧은 텍스트를 비교합니다.
    """
    short_norm = normalize_text(short_text)
    long_norm = normalize_text(long_text)

    if not short_norm or not long_norm:
        return False, 0.0

    # 짧은 텍스트가 더 긴 경우 swap
    if len(short_norm) > len(long_norm):
        short_norm, long_norm = long_norm, short_norm

    # 전체 비교 (빠른 체크)
    if short_norm in long_norm:
        return True, 1.0

    # Sliding window: 긴 텍스트에서 짧은 텍스트 길이만큼의 창을 이동하며 비교
    window_size = len(short_norm)
    step = max(window_size // 4, 100)  # 성능을 위해 적절한 step
    best_ratio = 0.0

    for i in range(0, len(long_norm) - window_size + 1, step):
        window = long_norm[i:i + window_size]
        ratio = SequenceMatcher(None, short_norm, window).ratio()
        best_ratio = max(best_ratio, ratio)

        if best_ratio >= threshold:
            return True, best_ratio

    return best_ratio >= threshold, best_ratio


def find_duplicates(new_transcript, existing_interviews):
    """새 영상의 트랜스크립트를 기존 영상들과 비교하여 중복을 찾습니다.

    Args:
        new_transcript: 새 영상의 텍스트
        existing_interviews: list of dict with keys: id, youtube_id, transcript, duration

    Returns:
        dict with keys: is_duplicate, parent_id, similarity
    """
    if not new_transcript:
        return {"is_duplicate": False, "parent_id": None, "similarity": 0.0}

    best_match = {"is_duplicate": False, "parent_id": None, "similarity": 0.0}

    for existing in existing_interviews:
        if not existing.get("transcript"):
            continue

        is_dup, ratio = is_subset(new_transcript, existing["transcript"])

        if ratio > best_match["similarity"]:
            best_match = {
                "is_duplicate": is_dup,
                "parent_id": existing["id"] if is_dup else None,
                "similarity": ratio,
            }

    return best_match


if __name__ == "__main__":
    # 테스트
    full_text = "Hello world this is a full interview about space and mars and the future of humanity"
    clip_text = "this is a full interview about space and mars"
    unrelated = "something completely different about cooking recipes"

    dup, score = is_subset(clip_text, full_text)
    print(f"Clip vs Full: duplicate={dup}, score={score:.2f}")

    dup2, score2 = is_subset(unrelated, full_text)
    print(f"Unrelated vs Full: duplicate={dup2}, score={score2:.2f}")
