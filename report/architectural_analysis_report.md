# 법률 AI 어시스턴트 프로젝트 아키텍처 분석 보고서

## 📋 개요

본 보고서는 LangGraph를 기반으로 한 법률 AI 어시스턴트 시스템의 전체 아키텍처, 컴포넌트 구조, 데이터 플로우 및 상호 연결 관계를 종합적으로 분석한 문서입니다.

**생성일**: 2024년 12월 26일  
**프로젝트명**: Legal AI Assistant with LangGraph  
**기술 스택**: LangGraph, Streamlit, ChromaDB, SQLite, OpenAI GPT-4o, HyperClova-X

---

## 🏗️ 전체 시스템 아키텍처

### 1. 계층별 구조 (Layered Architecture)

```
┌─────────────────────────────────────────────────┐
│                 Frontend Layer                   │
│              (Streamlit App)                     │
├─────────────────────────────────────────────────┤
│               Workflow Layer                     │
│             (LangGraph Nodes)                    │
├─────────────────────────────────────────────────┤
│                Core Services                     │
│        (DB, Vector Store, LLM, Embeddings)      │
├─────────────────────────────────────────────────┤
│                 Data Layer                       │
│           (SQLite, ChromaDB)                     │
└─────────────────────────────────────────────────┘
```

### 2. 핵심 컴포넌트

#### A. Frontend Layer
- **Streamlit App** (`app/main.py`)
  - 문서 검색 탭
  - 문서 분석 탭
  - 법률 Q&A 탭
  - 시스템 상태 탭

#### B. Workflow Layer (LangGraph)
- **Legal Workflow** (`workflows/graphs/legal_workflow.py`)
- **Retrieval Node** (`workflows/nodes/retrieval.py`)
- **Analysis Node** (`workflows/nodes/analysis.py`)
- **State Management** (`workflows/graphs/legal_workflow_state.py`)

#### C. Core Services
- **Database Manager** (`core/database/sqlite.py`)
- **Vector Store Manager** (`core/database/vector_store.py`)
- **LLM Clients** (`core/llm/`)
- **Embeddings** (`core/embeddings/kure_embeddings.py`)

#### D. Data Layer
- **SQLite Database**: 구조화된 문서 메타데이터
- **ChromaDB**: 벡터 임베딩 저장소

---

## 🔄 LangGraph 워크플로우 분석

### 1. 메인 워크플로우 구조

```python
# legal_workflow.py의 핵심 구조
workflow = StateGraph(LegalWorkflowState)
workflow.add_node("retrieval", run_retrieval)
workflow.add_node("analysis", run_analysis)
workflow.set_entry_point("retrieval")
workflow.add_edge("retrieval", "analysis")
workflow.add_edge("analysis", END)
```

### 2. 노드별 상세 분석

#### A. Retrieval Node
**역할**: 문서 검색 및 정보 검색
**주요 기능**:
- PostgreSQL 텍스트 검색
- 벡터 유사도 검색
- 하이브리드 결과 조합
- BGE 리랭킹

**상태 전이**:
```
RetrievalState {
  query → postgres_results → vector_results → 
  hybrid_results → reranked_results → final_results
}
```

#### B. Analysis Node
**역할**: 문서 분석 및 인사이트 추출
**주요 기능**:
- 문서 요약
- 핵심 포인트 추출
- 법적 쟁점 식별
- 개체명 인식
- 위험도 평가
- 권고사항 생성

**상태 전이**:
```
AnalysisState {
  document_content → summary → key_points → 
  legal_issues → entities → analysis_result
}
```

### 3. 상태 관리 (State Management)

#### LegalWorkflowState
```python
class LegalWorkflowState(TypedDict):
    query: str                              # 사용자 쿼리
    documents: List[Dict[str, Any]]         # 원본 문서들
    retrieved_docs: List[Dict[str, Any]]    # 검색된 문서들
    analysis_result: Dict[str, Any]         # 분석 결과
    messages: List[BaseMessage]             # 메시지 기록
    current_step: Optional[str]             # 현재 단계
    error: Optional[str]                    # 오류 정보
    metadata: Optional[Dict[str, Any]]      # 메타데이터
```

---

## 🔗 컴포넌트 간 연결 관계

### 1. 데이터 플로우

```
사용자 입력 → Streamlit App → Legal Workflow → 
Retrieval Node → [SQLite + Vector Store] → 
Analysis Node → LLM Client → 최종 결과
```

### 2. 서비스 의존성 그래프

```
Legal Workflow
├── Retrieval Node
│   ├── SQLite Manager
│   ├── Vector Store Manager
│   │   └── KURE Embeddings
│   └── BGE Reranker
└── Analysis Node
    ├── OpenAI Client
    └── Clova Client
```

### 3. 상태 전파 메커니즘

1. **초기 상태**: 사용자 쿼리로 LegalWorkflowState 생성
2. **검색 단계**: RetrievalState로 상태 변환 후 검색 수행
3. **분석 단계**: AnalysisState로 상태 변환 후 분석 수행
4. **결과 통합**: 최종 결과를 LegalWorkflowState에 병합

---

## 🗄️ 데이터베이스 아키텍처

### 1. SQLite Database
**용도**: 구조화된 문서 메타데이터 저장
**스키마**:
```sql
CREATE TABLE legal_documents (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    document_type TEXT,
    category TEXT,
    source TEXT,
    author TEXT,
    date_published DATETIME,
    doc_metadata JSON,
    tags TEXT
);
```

### 2. ChromaDB Vector Store
**용도**: 문서 임베딩 벡터 저장 및 유사도 검색
**특징**:
- 컬렉션명: "legal_documents"
- 임베딩 모델: KURE-v1 (한국어 특화)
- 메타데이터 포함 저장

---

## 🧠 LLM 클라이언트 아키텍처

### 1. Multi-LLM 지원 구조

```python
class LLMProvider:
    ├── OpenAI Client (GPT-4o)
    └── Clova Client (HyperClova-X)
```

### 2. 공통 인터페이스

모든 LLM 클라이언트는 다음 메서드를 구현:
- `chat_completion()`
- `analyze_legal_document()`
- `answer_legal_question()`
- `summarize_text()`
- `extract_key_points()`

---

## 🔍 검색 시스템 분석

### 1. 하이브리드 검색 전략

```
Query Input
├── PostgreSQL FTS (전문 검색)
├── Vector Similarity (의미적 검색)
└── Hybrid Fusion → Reranking → Final Results
```

### 2. 검색 파이프라인

1. **전처리**: 쿼리 정규화 및 토큰화
2. **병렬 검색**: SQL 검색과 벡터 검색 동시 수행
3. **결과 융합**: 스코어 기반 하이브리드 조합
4. **리랭킹**: BGE 모델을 사용한 재순위화
5. **후처리**: 최종 결과 포맷팅

---

## 📊 성능 및 확장성 분석

### 1. 현재 성능 특성

**장점**:
- LangGraph를 통한 모듈화된 워크플로우
- 하이브리드 검색으로 높은 검색 정확도
- 다중 LLM 지원으로 유연성 확보
- 한국어 특화 임베딩 모델 사용

**병목 지점**:
- LLM API 호출 지연시간
- 대용량 문서 처리 시 메모리 사용량
- 벡터 검색 시 임베딩 생성 시간

### 2. 확장성 고려사항

**수평 확장**:
- LLM 클라이언트 로드 밸런싱
- 벡터 DB 샤딩
- 캐싱 레이어 추가

**수직 확장**:
- GPU 활용 임베딩 가속화
- 인메모리 벡터 인덱스
- 배치 처리 최적화

---

## 🔧 설정 및 환경 관리

### 1. 설정 구조 (`core/simple_config.py`)

```python
class Settings:
    app_title: str
    database_url: str
    chroma_persist_directory: str
    embedding_model: str
    openai_api_key: str
    clova_api_key: str
    debug: bool
```

### 2. 환경별 설정

- **개발 환경**: 로컬 SQLite + 로컬 ChromaDB
- **운영 환경**: 확장 가능한 DB + 클라우드 벡터 DB

---

## 🚨 오류 처리 및 복구

### 1. 오류 처리 전략

```python
# 워크플로우 레벨 오류 처리
def handle_error(state: LegalWorkflowState) -> Dict[str, Any]:
    error_msg = state.get("error", "Unknown error occurred")
    return {
        "messages": state["messages"] + [
            AIMessage(content=f"오류가 발생했습니다: {error_msg}")
        ],
        "current_step": "error_handled"
    }
```

### 2. 복구 메커니즘

- **Graceful Degradation**: LLM 서비스 장애 시 대체 모델 사용
- **Fallback Strategy**: 벡터 검색 실패 시 키워드 검색으로 대체
- **State Preservation**: 오류 발생 시 상태 보존 및 재시작 지원

---

## 📈 개선 제안사항

### 1. 단기 개선사항

1. **캐싱 시스템 도입**
   - Redis를 활용한 LLM 응답 캐싱
   - 임베딩 벡터 캐싱

2. **모니터링 강화**
   - 워크플로우 실행 시간 추적
   - 검색 성능 메트릭 수집

3. **UI/UX 개선**
   - 실시간 진행 상황 표시
   - 결과 시각화 강화

### 2. 중장기 개선사항

1. **분산 처리 아키텍처**
   - Celery를 이용한 비동기 작업 처리
   - 마이크로서비스 분리

2. **고급 검색 기능**
   - 의미적 검색 고도화
   - 다모달 검색 지원 (텍스트 + 이미지)

3. **AI 모델 최적화**
   - 도메인 특화 모델 파인튜닝
   - 엣지 배포를 위한 모델 경량화

---

## 🔐 보안 및 규정 준수

### 1. 데이터 보안

- API 키 환경변수 관리
- 민감 정보 로깅 방지
- 데이터 암호화 (전송/저장)

### 2. 법적 준수

- 개인정보보호법 준수
- 법률 서비스 제공 관련 규정 검토
- 데이터 보존 정책 수립

---

## 📋 결론

본 법률 AI 어시스턴트 시스템은 LangGraph를 중심으로 한 모듈화된 아키텍처를 통해 확장성과 유지보수성을 확보하고 있습니다. 하이브리드 검색 시스템과 다중 LLM 지원을 통해 높은 품질의 법률 정보 서비스를 제공할 수 있는 기반을 구축하였습니다.

향후 제안된 개선사항들을 단계적으로 적용한다면, 더욱 강력하고 신뢰할 수 있는 법률 AI 플랫폼으로 발전시킬 수 있을 것입니다.

---

**보고서 작성자**: AI Assistant  
**검토일**: 2024년 12월 26일 