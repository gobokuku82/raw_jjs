# Legal AI Assistant MVP

법률회사용 Streamlit 기반 AI 어시스턴트 (MVP 버전)

[![MVP Version](https://img.shields.io/badge/version-MVP%20v1.0.0-green.svg)](https://github.com/your-repo/legal-ai-assistant)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46.1-FF4B4B.svg)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org/)

## 🎯 주요 특징

- **🚀 즉시 실행**: Docker 없이 로컬에서 바로 실행 가능
- **📖 하이브리드 검색**: SQLite + ChromaDB 벡터 검색
- **📊 문서 분석**: 법률 문서의 핵심 요약, 쟁점 분석
- **❓ 법률 Q&A**: 상황별 법률 질문에 대한 AI 답변
- **🤖 다중 LLM 지원**: OpenAI GPT-4o, HyperClova-X
- **🔧 간단 설정**: API 키 없이도 기본 기능 사용 가능

## 🏗️ MVP 아키텍처

```
legal_ai_app/
├── app/main.py                     # Streamlit 메인 앱
├── core/
│   ├── simple_config.py           # 간단한 설정 관리
│   ├── models/simple_models.py    # dataclass 기반 모델
│   ├── database/sqlite.py         # SQLite 데이터베이스
│   ├── embeddings/                # KURE-v1, BGE 리랭커
│   └── llm/                      # OpenAI, HyperClova-X
├── data/                          # SQLite DB, ChromaDB 저장
└── test_system.py                 # 시스템 테스트 스크립트
```

## 🚀 빠른 시작 (3단계)

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 시스템 테스트
```bash
python test_system.py
```

### 3. 앱 실행
```bash
streamlit run app/main.py
```

브라우저에서 `http://localhost:8501`로 접속 🎉

## 🔧 선택적 설정

### 환경 변수 (.env) - 선택사항
```env
# API Keys (선택사항 - 없어도 기본 기능 사용 가능)
OPENAI_API_KEY=your_openai_api_key_here
CLOVA_API_KEY=your_naver_clova_api_key_here

# 데이터베이스 (기본값 사용 권장)
DATABASE_URL=sqlite:///./data/legal_ai.db
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# 모델 설정 (기본값 사용 권장)
EMBEDDING_MODEL=nlpai-lab/KURE-v1
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
```

> 💡 **Tip**: `.env` 파일 없이도 모든 기능이 정상 작동합니다!

## 📚 사용 방법

### 1. 문서 검색 🔍
- 검색어 입력하여 관련 법률 문서 찾기
- SQLite 텍스트 검색 + ChromaDB 벡터 검색
- BGE 리랭커로 정확도 향상

### 2. 문서 분석 📊
- 텍스트 직접 입력 또는 파일 업로드
- 요약, 핵심 사항, 법적 쟁점 자동 추출
- 위험도 평가 및 권고사항 제공

### 3. 법률 Q&A ❓
- 자연어로 법률 질문 입력
- 관련 문서 검색 후 맥락 기반 답변
- 참고 문서와 함께 결과 제공

### 4. 시스템 상태 ⚙️
- 실시간 시스템 모니터링
- 데이터베이스 연결 상태 확인
- AI 모델 상태 체크

## 🛠️ 기술 스택

### 🔥 최신 기술
- **LangChain**: 0.3.26 (최신 버전)
- **LangGraph**: 0.5.0 (최신 버전)
- **Streamlit**: 1.46.1 (최신 버전)
- **ChromaDB**: 1.0.13 (최신 벡터 DB)

### 🗄️ 데이터베이스
- **SQLite**: 로컬 정형 데이터
- **ChromaDB**: 벡터 저장소

### 🤖 AI 모델
- **Embeddings**: nlpai-lab/KURE-v1 (한국어 특화)
- **Reranker**: BAAI/bge-reranker-v2-m3 (정확도 향상)
- **LLM**: OpenAI GPT-4o, HyperClova-X

## 📊 샘플 데이터

MVP 버전에는 기본 샘플 데이터가 포함되어 있습니다:

- **민법**: 민법 제1조 (목적)
- **판례**: 계약의 성립 관련 판례  
- **가이드**: 근로계약서 작성 가이드

## ⚡ 성능 & 최적화

- **빠른 시작**: Docker 없이 즉시 실행
- **가벼운 구조**: SQLite 로컬 데이터베이스
- **효율적 검색**: 하이브리드 검색 + 리랭킹
- **메모리 최적화**: 배치 처리 및 캐싱

## 🧪 테스트 결과

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

## 🐛 문제 해결

### 일반적인 문제들

**Q: 패키지 설치 오류가 발생해요**
```bash
# 가상환경 사용 권장
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

**Q: Streamlit이 실행되지 않아요**
```bash
# 포트 변경 시도
streamlit run app/main.py --server.port 8502
```

**Q: 임베딩 모델 로딩이 느려요**
- 첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다
- 이후 실행은 빠릅니다

## 🔮 향후 개발 계획

### 🎯 다음 버전 (v1.1.0)
- [ ] 웹 UI 개선 및 사용성 향상
- [ ] 더 많은 샘플 법률 데이터 추가
- [ ] 파일 업로드 기능 강화
- [ ] 검색 결과 내보내기 (PDF, Excel)

### 🚀 장기 로드맵
- [ ] REST API 서버 버전
- [ ] 사용자 인증 및 권한 관리
- [ ] 클라우드 배포 버전
- [ ] 고급 법률 분석 기능

## 📄 라이선스

MIT License - 자유롭게 사용하세요!

## 🤝 기여하기

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Legal AI Assistant MVP** - 법률 업무를 위한 간단하고 강력한 AI 도구 ⚖️

*Made with ❤️ for legal professionals* 