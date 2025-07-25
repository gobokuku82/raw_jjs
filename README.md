# Legal AI Assistant

법률회사를 위한 LangGraph + MCP 기반 AI 어시스턴트입니다.

## 🎯 주요 기능

- **📖 문서 검색**: 하이브리드 검색 (PostgreSQL + 벡터 DB + 리랭킹)
- **📊 문서 분석**: 법률 문서의 핵심 요약, 쟁점 분석, 위험도 평가
- **❓ 법률 Q&A**: 상황별 법률 질문에 대한 AI 답변
- **🤖 다중 LLM 지원**: OpenAI GPT-4o, HyperClova-X

## 🏗️ 시스템 아키텍처

```
legal_ai_app/
├── app/                    # Streamlit 애플리케이션
├── core/                   # 핵심 구성요소
│   ├── config.py          # 설정 관리
│   ├── database/          # 데이터베이스 (PostgreSQL, ChromaDB)
│   ├── embeddings/        # 임베딩 (KURE-v1, BGE 리랭커)
│   ├── llm/              # LLM 클라이언트 (OpenAI, HyperClova-X)
│   └── models/           # 데이터 모델
├── langgraph/             # LangGraph 워크플로우
│   ├── nodes/            # 검색, 분석 노드
│   └── graphs/           # 워크플로우 정의
├── mcp/                  # MCP 서버
│   └── servers/          # 법률 DB, 문서 처리 서버
└── data/                 # 데이터 및 스키마
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 API 키 설정
```

### 2. 데이터베이스 설정

```bash
# PostgreSQL 시작 (Docker)
docker-compose up -d

# 테이블 생성 및 샘플 데이터 삽입
docker exec -i postgres_container psql -U legal_user -d legal_ai_db < data/schemas/init.sql
```

### 3. 애플리케이션 실행

```bash
# Streamlit 앱 실행
streamlit run app/main.py
```

브라우저에서 `http://localhost:8501`로 접속

## 🔧 설정

### 환경 변수 (.env)

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# HyperClova-X API (선택사항)
CLOVA_API_KEY=your_clova_api_key_here
CLOVA_APIGW_API_KEY=your_clova_apigw_key_here

# 데이터베이스
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=legal_ai_db
POSTGRES_USER=legal_user
POSTGRES_PASSWORD=legal_password

# 벡터 데이터베이스
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# 모델 설정
EMBEDDING_MODEL=nlpai-lab/KURE-v1
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
```

## 📚 사용 방법

### 1. 문서 검색
- 검색어 입력하여 관련 법률 문서 찾기
- 하이브리드 검색으로 정확한 결과 제공
- 관련도 점수로 정렬된 결과

### 2. 문서 분석
- 텍스트 직접 입력 또는 파일 업로드
- 요약, 핵심 사항, 법적 쟁점 자동 추출
- 위험도 평가 및 권고사항 제공

### 3. 법률 Q&A
- 자연어로 법률 질문 입력
- 관련 문서 검색 후 맥락 기반 답변
- 참고 문서와 함께 결과 제공

## 🛠️ 기술 스택

### Core Technologies
- **LangGraph**: 워크플로우 오케스트레이션
- **MCP (Model Context Protocol)**: 모델 통신 프로토콜
- **Streamlit**: 웹 애플리케이션 프레임워크

### Databases
- **PostgreSQL**: 정형 데이터 저장
- **ChromaDB**: 벡터 데이터베이스

### AI Models
- **Embeddings**: nlpai-lab/KURE-v1 (한국어 특화)
- **Reranker**: BAAI/bge-reranker-v2-m3
- **LLM**: OpenAI GPT-4o, HyperClova-X

### Additional Tools
- **Docker**: 개발 환경 컨테이너화
- **SQLAlchemy**: ORM
- **Pydantic**: 데이터 검증

## 📊 LangGraph 워크플로우

### 문서 검색 워크플로우
```
검색 요청 → PostgreSQL 검색 → 벡터 검색 → 결과 병합 → 리랭킹 → 최종 결과
```

### 문서 분석 워크플로우
```
문서 입력 → 요약 추출 → 핵심 사항 → 법적 쟁점 → 개체명 인식 → 권고사항 → 위험도 평가
```

## 🤖 MCP 서버

### Legal Database Server
- 문서 검색 및 관리
- 하이브리드 검색 기능
- 문서 분석 도구

### Document Processor Server
- 파일 업로드 및 텍스트 추출
- 문서 전처리 및 청킹
- 메타데이터 추출

## ⚡ 성능 최적화

- **벡터 인덱싱**: ChromaDB 영구 저장
- **SQL 인덱스**: 제목, 유형, 카테고리별 인덱스
- **텍스트 검색**: PostgreSQL GIN 인덱스
- **리랭킹**: BGE 모델로 정확도 향상

## 📈 모니터링

- 시스템 상태 탭에서 실시간 모니터링
- 데이터베이스 연결 상태 확인
- 모델 availability 체크
- 성능 메트릭 표시

## 🔒 보안 고려사항

- API 키는 환경 변수로 관리
- .env 파일은 git에서 제외
- 데이터베이스 접근 권한 제한
- 입력 데이터 검증

## 🧪 테스트

```bash
# 단위 테스트 실행
pytest tests/

# 특정 모듈 테스트
pytest tests/test_retrieval.py
```

## 📝 추가 개발 계획

- [ ] 더 많은 파일 형식 지원 (PDF, DOCX)
- [ ] 사용자 인증 및 권한 관리
- [ ] 문서 버전 관리
- [ ] REST API 제공
- [ ] 성능 최적화 및 캐싱
- [ ] 다국어 지원 확장

## 🤝 기여 방법

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 등록해 주세요.

---

**Legal AI Assistant** - 법률 업무의 효율성을 높이는 AI 솔루션 #   r a w _ j j s  
 