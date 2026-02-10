"""
Main Pipeline — 크롤링 -> 텍스트 변환 -> 중복 판별 -> DB 저장

사용법:
  python main.py crawl        # 새 인터뷰 검색 및 메타데이터 수집
  python main.py transcribe   # 트랜스크립트가 없는 영상의 텍스트 변환
  python main.py dedup        # 중복 영상 판별
  python main.py full         # 전체 파이프라인 실행
"""
import sys
import psycopg2
import psycopg2.extras
from config import DATABASE_URL
from crawler import crawl_all
from transcriber import transcribe
from dedup import find_duplicates


def get_db():
    """PostgreSQL 연결을 반환합니다."""
    return psycopg2.connect(DATABASE_URL)


def save_interviews(videos):
    """크롤링한 메타데이터를 DB에 저장합니다 (중복 youtube_id는 스킵)."""
    conn = get_db()
    cur = conn.cursor()
    inserted = 0

    for v in videos:
        try:
            cur.execute("""
                INSERT INTO interviews (youtube_id, title, interview_date, interviewer,
                    summary, youtube_url, thumbnail_url, duration, channel_name,
                    channel_id, is_original, created_at, updated_at)
                VALUES (%(youtube_id)s, %(title)s, %(interview_date)s, %(interviewer)s,
                    %(summary)s, %(youtube_url)s, %(thumbnail_url)s, %(duration)s,
                    %(channel_name)s, %(channel_id)s, %(is_original)s, NOW(), NOW())
                ON CONFLICT (youtube_id) DO NOTHING
            """, v)
            if cur.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"[DB] Error saving {v.get('youtube_id')}: {e}")
            conn.rollback()
            continue

    conn.commit()
    cur.close()
    conn.close()
    print(f"[DB] Inserted {inserted} new interviews")
    return inserted


def run_transcriptions():
    """트랜스크립트가 없는 영상들을 텍스트 변환합니다."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, youtube_id FROM interviews WHERE transcript IS NULL AND is_original = true")
    rows = cur.fetchall()
    print(f"[TRANSCRIBE] {len(rows)} interviews need transcription")

    for row in rows:
        youtube_id = row["youtube_id"]
        print(f"[TRANSCRIBE] Processing: {youtube_id}")
        text = transcribe(youtube_id)
        if text:
            cur.execute("UPDATE interviews SET transcript = %s, updated_at = NOW() WHERE id = %s",
                        (text, row["id"]))
            conn.commit()
            print(f"[TRANSCRIBE] Done: {youtube_id} ({len(text)} chars)")
        else:
            print(f"[TRANSCRIBE] Failed: {youtube_id}")

    cur.close()
    conn.close()


def run_dedup():
    """중복 영상을 판별합니다."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # 트랜스크립트가 있는 원본 영상 로드
    cur.execute("""
        SELECT id, youtube_id, transcript, duration
        FROM interviews
        WHERE transcript IS NOT NULL AND is_original = true
        ORDER BY duration DESC
    """)
    originals = [dict(r) for r in cur.fetchall()]
    print(f"[DEDUP] Checking {len(originals)} interviews for duplicates")

    for i, video in enumerate(originals):
        # 자기보다 긴 영상들과 비교 (자신 제외)
        others = [o for o in originals if o["id"] != video["id"] and o["duration"] >= video["duration"]]
        result = find_duplicates(video["transcript"], others)

        if result["is_duplicate"]:
            print(f"[DEDUP] DUPLICATE: {video['youtube_id']} (sim={result['similarity']:.2f}) -> parent={result['parent_id']}")
            cur.execute("""
                UPDATE interviews SET is_original = false, parent_id = %s, updated_at = NOW()
                WHERE id = %s
            """, (result["parent_id"], video["id"]))
            conn.commit()

    cur.close()
    conn.close()
    print("[DEDUP] Done")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "crawl":
        videos = crawl_all()
        save_interviews(videos)
    elif command == "transcribe":
        run_transcriptions()
    elif command == "dedup":
        run_dedup()
    elif command == "full":
        print("=== Step 1: Crawl ===")
        videos = crawl_all()
        save_interviews(videos)
        print("\n=== Step 2: Transcribe ===")
        run_transcriptions()
        print("\n=== Step 3: Dedup ===")
        run_dedup()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
