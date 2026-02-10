# Elon Musk Interview Timeline - Implementation Plan

## Project Overview
일론 머스크의 인터뷰를 시간순으로 정리한 세로 타임라인 웹사이트.
- 세로 타임라인 UI (날짜 / 인터뷰 주체 / 제목 / 한줄요약)
- 클릭 시 유튜브 링크로 이동
- 자동 크롤링 서버
- 텍스트 기반 중복/클립 영상 감지 시스템

## Tech Stack
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Backend API**: Next.js API Routes
- **Crawler/Worker**: Python (yt-dlp + Whisper)
- **Database**: SQLite (Prisma ORM) - 초기 단계에 적합, 추후 PostgreSQL 마이그레이션 가능
- **Text Similarity**: Python (difflib + optional vector embedding)

## Directory Structure
```
elon-interview/
├── frontend/                    # Next.js app
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # 메인 타임라인 페이지
│   │   │   ├── layout.tsx       # 레이아웃
│   │   │   ├── globals.css      # 전역 스타일
│   │   │   └── api/
│   │   │       └── interviews/
│   │   │           └── route.ts # 인터뷰 목록 API
│   │   ├── components/
│   │   │   ├── Timeline.tsx     # 타임라인 컴포넌트
│   │   │   ├── TimelineItem.tsx # 개별 인터뷰 카드
│   │   │   ├── Header.tsx       # 헤더
│   │   │   └── FilterBar.tsx    # 연도/채널 필터
│   │   ├── lib/
│   │   │   └── db.ts            # DB 연결
│   │   └── types/
│   │       └── interview.ts     # 타입 정의
│   ├── prisma/
│   │   └── schema.prisma        # DB 스키마
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── crawler/                     # Python 크롤러
│   ├── crawler.py               # YouTube 검색 및 메타데이터 수집
│   ├── transcriber.py           # Whisper STT (음성→텍스트)
│   ├── dedup.py                 # 중복 판별 엔진
│   ├── main.py                  # 크롤러 메인 진입점
│   ├── requirements.txt         # Python 의존성
│   └── config.py                # 설정 (API 키 등)
│
├── data/
│   └── seed.json                # 초기 시드 데이터 (수동 큐레이션된 주요 인터뷰 목록)
│
└── README.md
```

---

## Implementation Steps

### Phase 1: 프로젝트 기초 세팅
1. **Next.js 프로젝트 초기화** (`frontend/`)
   - `npx create-next-app@latest` with TypeScript + Tailwind
   - ESLint, Prettier 설정
2. **Prisma + SQLite 세팅**
   - Interview 모델 정의 (id, youtubeId, title, date, interviewer, summary, youtubeUrl, thumbnailUrl, duration, transcript, isOriginal, parentId)
3. **시드 데이터 준비** (`data/seed.json`)
   - 주요 인터뷰 10~20개를 수동으로 정리 (날짜, 제목, 유튜브 링크, 인터뷰어, 한줄 요약)

### Phase 2: 프론트엔드 타임라인 UI
4. **타임라인 메인 컴포넌트 구현** (`Timeline.tsx`)
   - 중앙 세로선 + 좌우 교차 카드 배치
   - 연도 구분 마커
   - 무한 스크롤 또는 연도별 섹션
5. **인터뷰 카드 컴포넌트** (`TimelineItem.tsx`)
   - 표시 정보: 날짜 | 인터뷰 주체(채널) | 제목 | 한줄 요약
   - 호버 시 썸네일 프리뷰
   - 클릭 시 유튜브 새 탭 열기
6. **필터/검색 기능** (`FilterBar.tsx`)
   - 연도별 필터
   - 인터뷰어/채널별 필터
   - 키워드 검색
7. **API 라우트** (`api/interviews/route.ts`)
   - GET: 인터뷰 목록 (페이지네이션, 필터링)
   - 시드 데이터 → DB 마이그레이션 스크립트

### Phase 3: Python 크롤러 서버
8. **YouTube 데이터 수집기** (`crawler.py`)
   - yt-dlp를 사용하여 "Elon Musk interview" 검색 결과 수집
   - 메타데이터 추출: 제목, 업로드 날짜, 채널명, 영상 길이, 설명란
   - 이미 DB에 있는 youtubeId는 스킵
9. **음성→텍스트 변환** (`transcriber.py`)
   - yt-dlp로 오디오만 다운로드 (mp3/wav)
   - OpenAI Whisper (base 또는 small 모델)로 텍스트 변환
   - 변환된 텍스트를 DB에 저장
10. **중복/클립 감지 엔진** (`dedup.py`)
    - **1차 필터**: 영상 길이 비교 (짧은 영상 → 클립 의심)
    - **2차 필터**: 텍스트 유사도 비교
      - 긴 영상의 텍스트 안에 짧은 영상의 텍스트가 포함되는지 확인
      - `difflib.SequenceMatcher` 또는 sliding window 방식
      - 유사도 80% 이상이면 중복으로 판정
    - **결과**: 원본 영상에 `isOriginal=True`, 클립에 `isOriginal=False` + `parentId=원본ID`
11. **크롤러 메인 파이프라인** (`main.py`)
    - 수집 → 텍스트 변환 → 중복 판별 → DB 저장 순서로 실행
    - CLI 또는 cron job으로 주기적 실행 가능

### Phase 4: 통합 및 마무리
12. **프론트엔드 ↔ DB 연동**
    - 타임라인에 `isOriginal=True`인 영상만 표시
    - 클립 영상은 원본 카드 하위에 "관련 클립 N개" 표시 (선택적)
13. **반응형 디자인**
    - 모바일: 한 줄 타임라인 (카드가 모두 오른쪽)
    - 데스크탑: 좌우 교차 배치
14. **배포 준비**
    - Next.js: Vercel 또는 Docker
    - 크롤러: Docker + cron schedule

---

## Database Schema (Prisma)
```prisma
model Interview {
  id           String    @id @default(cuid())
  youtubeId    String    @unique
  title        String
  date         DateTime
  interviewer  String        // 인터뷰 주체 (예: "Joe Rogan", "Lex Fridman")
  summary      String        // 한줄 요약
  youtubeUrl   String
  thumbnailUrl String?
  duration     Int           // 영상 길이 (초)
  transcript   String?       // STT 결과 텍스트
  isOriginal   Boolean   @default(true)
  parentId     String?       // 원본 영상 ID (클립인 경우)
  parent       Interview? @relation("ClipRelation", fields: [parentId], references: [id])
  clips        Interview[] @relation("ClipRelation")
  channelName  String?
  channelId    String?
  createdAt    DateTime  @default(now())
  updatedAt    DateTime  @updatedAt
}
```

## Seed Data (예시)
```json
[
  {
    "youtubeId": "DxREm3s1scA",
    "title": "Elon Musk: SpaceX, Mars, Tesla Autopilot, Self-Driving, Robotics, and AI",
    "date": "2023-11-09",
    "interviewer": "Lex Fridman",
    "summary": "SpaceX의 화성 계획, 테슬라 자율주행, AI 안전성에 대한 4시간 심층 인터뷰",
    "youtubeUrl": "https://www.youtube.com/watch?v=DxREm3s1scA",
    "duration": 14400
  }
]
```

---

## Scope for This Session
이번 세션에서는 **Phase 1 + Phase 2**를 구현합니다:
- Next.js 프로젝트 세팅
- Prisma + SQLite DB 세팅
- 시드 데이터 준비 (주요 인터뷰 15~20개)
- 타임라인 UI 전체 구현 (세로 타임라인, 카드, 필터)
- API 라우트 구현
- 반응형 디자인

Phase 3 (Python 크롤러)는 별도 세션에서 진행할 수 있도록 구조만 잡아둡니다.
