# Legal AI Assistant - MVP 패치노트

## 버전: MVP v1.0.0
**릴리스 날짜:** 2025-06-28

---

## 🎯 주요 변경사항

### 📱 **MVP 아키텍처로 간소화**
- **Streamlit 단일 프레임워크**: FastAPI 제거, Streamlit만 사용하는 간단한 구조
- **SQLite 데이터베이스**: PostgreSQL 대신 SQLite로 변경하여 설치 및 설정 간소화
- **Pydantic 제거**: dataclass를 사용한 단순한 데이터 모델로 변경
- **Docker 제거**: 로컬 개발에 집중, 복잡한 컨테이너 설정 제거

### 🔧 **기술 스택 업데이트**
- **LangChain**: 0.3.26 (최신 버전)
- **LangGraph**: 0.5.0 (최신 버전)
- **Streamlit**: 1.46.1 (최신 버전)
- **ChromaDB**: 1.0.13 (최신 벡터 데이터베이스)

### 📊 **데이터베이스 구조**
- **SQLite**: `./data/legal_ai.db` 경로에 로컬 데이터베이스
- **ChromaDB**: `./data/chroma_db` 경로에 벡터 저장소
- **자동 테이블 생성**: 첫 실행 시 자동으로 데이터베이스 테이블 생성

---

## ✨ **새로운 기능**

### 🚀 **시스템 테스트 스크립트**
- `test_system.py`: 전체 시스템의 기본 기능 검증
- 자동화된 샘플 데이터 생성
- 데이터베이스 연결 및 테이블 생성 확인
- 임베딩 모델 및 LLM 클라이언트 로딩 검증

### 🗃️ **샘플 법률 데이터**
- **민법**: 민법 제1조 (목적)
- **판례**: 계약의 성립 관련 판례
- **가이드**: 근로계약서 작성 가이드

### 🔍 **하이브리드 검색 시스템**
- SQLite LIKE 검색 + ChromaDB 벡터 검색
- BGE 리랭커를 통한 검색 결과 정렬
- KURE-v1 한국어 특화 임베딩 모델

---

## 🔄 **구조적 변경**

### 📁 **파일 구조 변경**
```
legal_ai_app/
├── app/main.py                     # Streamlit 메인 앱
├── core/
│   ├── simple_config.py           # 간단한 설정 관리 (Pydantic 없음)
│   ├── models/simple_models.py    # dataclass 기반 모델
│   ├── database/sqlite.py         # SQLite 데이터베이스 매니저
│   ├── embeddings/                # KURE-v1, BGE 리랭커
│   └── llm/                      # OpenAI, HyperClova-X
├── data/                          # SQLite DB, ChromaDB 저장
└── test_system.py                 # 시스템 테스트 스크립트
```

### 🗑️ **제거된 파일들**
- `docker-compose.yml`: Docker 설정 제거
- `core/database/postgres.py`: PostgreSQL 매니저 제거
- `data/schemas/init.sql`: PostgreSQL 초기화 스크립트 제거
- `core/models/legal_document.py`: Pydantic 모델 제거

---

## 🛠️ **설정 및 환경변수**

### 📝 **환경변수 (선택사항)**
```env
# API Keys (선택사항)
OPENAI_API_KEY=your_openai_api_key_here
CLOVA_API_KEY=your_naver_clova_api_key_here

# 데이터베이스 (기본값 사용 가능)
DATABASE_URL=sqlite:///./data/legal_ai.db
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# 모델 설정 (기본값 사용 가능)
EMBEDDING_MODEL=nlpai-lab/KURE-v1
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
```

### 🎯 **기본값 정책**
- API 키 없이도 기본 기능 사용 가능 (demo_key 사용)
- 모든 설정에 합리적인 기본값 제공
- `.env` 파일 없이도 정상 작동

---

## 🚀 **설치 및 실행**

### 1️⃣ **패키지 설치**
```bash
pip install -r requirements.txt
```

### 2️⃣ **시스템 테스트**
```bash
python test_system.py
```

### 3️⃣ **Streamlit 앱 실행**
```bash
streamlit run app/main.py
```

---

## 🐛 **버그 수정**

### ✅ **해결된 문제들**
- **Pydantic 버전 충돌**: BaseSettings 이전 문제 해결
- **SQLAlchemy metadata 충돌**: 예약어 문제 해결 (`doc_metadata`로 변경)
- **PostgreSQL 의존성**: SQLite로 완전 대체
- **Docker 복잡성**: 로컬 개발 환경으로 간소화

### ⚡ **성능 개선**
- **빠른 시작**: Docker 없이 즉시 실행 가능
- **가벼운 구조**: 불필요한 의존성 제거
- **로컬 최적화**: SQLite + ChromaDB 로컬 저장

---

## 📋 **테스트 결과**

```
==================================================
Legal AI Assistant - System Test
==================================================
Testing imports...
✓ Config loaded
✓ Database managers imported
✓ Models imported
✓ LLM clients imported
✓ Embedding models imported

Testing database creation...
✓ Database tables created successfully

Testing vector store...
✓ Vector store initialized successfully

Adding sample legal documents...
✓ Created document: 민법 제1조 (목적)
✓ Created document: 계약의 성립
✓ Created document: 근로계약서 작성 가이드

==================================================
Test Results: 4/4 passed
🎉 All tests passed! System is ready.
```

---

## 🔮 **향후 계획**

### 📈 **다음 버전 예정 기능**
- 웹 UI 개선 및 사용성 향상
- 더 많은 샘플 법률 데이터 추가
- 문서 업로드 기능
- 법률 분석 결과 시각화
- 사용자 피드백 시스템

### 🎯 **장기 로드맵**
- API 서버 버전 개발
- 다중 사용자 지원
- 클라우드 배포 버전
- 고급 법률 분석 기능

---

## 👥 **개발팀 노트**

이번 MVP 버전은 **단순함과 실용성**에 중점을 둔 리팩토링입니다. 복잡한 설정 없이 바로 사용할 수 있는 법률 AI 어시스턴트를 목표로 했습니다.

**핵심 원칙:**
- ✅ 설치가 쉬워야 한다
- ✅ 설정이 간단해야 한다  
- ✅ 즉시 사용할 수 있어야 한다
- ✅ 기본 기능이 완전해야 한다

---

*Legal AI Assistant MVP v1.0.0 - 2025년 6월 28일* 