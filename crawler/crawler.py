"""
YouTube Crawler — yt-dlp를 사용하여 Elon Musk 인터뷰 메타데이터를 수집합니다.
"""
import json
import subprocess
from datetime import datetime
from config import SEARCH_QUERIES, MIN_DURATION


def search_youtube(query, max_results=50):
    """yt-dlp로 YouTube 검색 결과의 메타데이터를 수집합니다."""
    cmd = [
        "yt-dlp",
        f"ytsearch{max_results}:{query}",
        "--dump-json",
        "--flat-playlist",
        "--no-download",
        "--quiet",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    videos = []

    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
            videos.append(data)
        except json.JSONDecodeError:
            continue

    return videos


def extract_metadata(video_data):
    """yt-dlp의 JSON 결과에서 필요한 메타데이터만 추출합니다."""
    youtube_id = video_data.get("id", "")
    duration = video_data.get("duration") or 0

    # 짧은 영상(클립/쇼츠) 필터링
    if duration < MIN_DURATION:
        return None

    upload_date = video_data.get("upload_date", "")
    interview_date = None
    if upload_date and len(upload_date) == 8:
        try:
            interview_date = datetime.strptime(upload_date, "%Y%m%d").date()
        except ValueError:
            pass

    return {
        "youtube_id": youtube_id,
        "title": video_data.get("title", ""),
        "interview_date": interview_date,
        "interviewer": None,  # 수동 입력 또는 NLP로 추출 필요
        "summary": video_data.get("description", "")[:200] if video_data.get("description") else None,
        "youtube_url": f"https://www.youtube.com/watch?v={youtube_id}",
        "thumbnail_url": f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg",
        "duration": duration,
        "channel_name": video_data.get("channel") or video_data.get("uploader"),
        "channel_id": video_data.get("channel_id"),
        "is_original": True,
    }


def crawl_all():
    """모든 검색 쿼리를 실행하고 결과를 통합합니다."""
    all_videos = {}

    for query in SEARCH_QUERIES:
        print(f"[CRAWL] Searching: {query}")
        results = search_youtube(query)
        for video in results:
            meta = extract_metadata(video)
            if meta and meta["youtube_id"] not in all_videos:
                all_videos[meta["youtube_id"]] = meta

    print(f"[CRAWL] Found {len(all_videos)} unique videos (>= {MIN_DURATION}s)")
    return list(all_videos.values())


if __name__ == "__main__":
    videos = crawl_all()
    for v in videos[:5]:
        print(f"  {v['interview_date']} | {v['channel_name']} | {v['title'][:60]}")
