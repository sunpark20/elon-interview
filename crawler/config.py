import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://root@localhost:5432/elon_interview_development"
)

# Whisper model: tiny, base, small, medium, large
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Duplicate detection threshold (0.0 ~ 1.0)
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.80"))

# YouTube search queries for crawling
SEARCH_QUERIES = [
    "Elon Musk full interview",
    "Elon Musk podcast full",
    "Elon Musk keynote speech",
    "Elon Musk conference talk",
]

# Minimum duration in seconds to filter out shorts/clips
MIN_DURATION = int(os.getenv("MIN_DURATION", "300"))  # 5 minutes

# Audio temp directory
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "tmp_audio")
