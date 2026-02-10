# Elon Musk Interview Timeline

## Tech Stack
- **Main Framework**: Ruby on Rails 8.1.2
- **Database**: PostgreSQL 16 (pgvector 확장 가능)
- **Frontend**: Hotwire/Turbo + Tailwind CSS v4
- **AI Worker**: Python (yt-dlp + Whisper)
- **Background Jobs**: Sidekiq + Redis (향후)

## 구현 상태

### Phase 1-2: 완료
- [x] Rails 프로젝트 + PostgreSQL + Tailwind CSS
- [x] Interview 모델 (self-referential parent/clips)
- [x] 시드 데이터 20개 (2013~2023)
- [x] 타임라인 UI (세로선 + 좌우 교차 카드 + 다크 테마)
- [x] 필터링 (연도, 인터뷰어, 키워드 검색)
- [x] 반응형 디자인

### Phase 3: 구조 완료
- [x] Python 크롤러 (`crawler/`)
  - `crawler.py` — YouTube 검색 및 메타데이터 수집
  - `transcriber.py` — Whisper STT
  - `dedup.py` — 텍스트 유사도 기반 중복 판별
  - `main.py` — 파이프라인 (crawl -> transcribe -> dedup)

### Phase 4: 향후
- [ ] Sidekiq + Redis
- [ ] ActiveAdmin 관리자 페이지
- [ ] pgvector 벡터 유사도 검색
- [ ] 자동 크롤링 스케줄링
- [ ] 배포

## 실행 방법
```bash
# DB 세팅
rails db:create db:migrate db:seed

# Tailwind 빌드
rails tailwindcss:build

# 서버 실행
rails server

# 크롤러 (Python)
cd crawler
pip install -r requirements.txt
python main.py full
```
