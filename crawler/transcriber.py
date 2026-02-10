"""
Transcriber — yt-dlp로 오디오를 다운로드하고 Whisper로 텍스트 변환합니다.
"""
import os
import subprocess
from config import WHISPER_MODEL, AUDIO_DIR

# Whisper는 실행 시 임포트 (GPU 메모리 절약)
_model = None


def _get_model():
    global _model
    if _model is None:
        import whisper
        print(f"[TRANSCRIBE] Loading Whisper model: {WHISPER_MODEL}")
        _model = whisper.load_model(WHISPER_MODEL)
    return _model


def download_audio(youtube_id):
    """yt-dlp로 영상의 오디오만 다운로드합니다."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    output_path = os.path.join(AUDIO_DIR, f"{youtube_id}.mp3")

    if os.path.exists(output_path):
        return output_path

    cmd = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={youtube_id}",
        "-x",  # Extract audio
        "--audio-format", "mp3",
        "--audio-quality", "5",  # Medium quality (절약)
        "-o", output_path,
        "--quiet",
    ]

    try:
        subprocess.run(cmd, check=True, timeout=300)
        return output_path
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"[TRANSCRIBE] Audio download failed for {youtube_id}: {e}")
        return None


def transcribe(youtube_id):
    """영상의 오디오를 다운로드하고 텍스트로 변환합니다."""
    audio_path = download_audio(youtube_id)
    if not audio_path or not os.path.exists(audio_path):
        return None

    print(f"[TRANSCRIBE] Transcribing: {youtube_id}")
    model = _get_model()
    result = model.transcribe(audio_path, language="en")

    # 임시 파일 정리
    try:
        os.remove(audio_path)
    except OSError:
        pass

    return result.get("text", "")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        vid = sys.argv[1]
        text = transcribe(vid)
        if text:
            print(f"[RESULT] {len(text)} characters")
            print(text[:500])
    else:
        print("Usage: python transcriber.py <youtube_id>")
