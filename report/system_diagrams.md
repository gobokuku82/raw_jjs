# 시스템 아키텍처 다이어그램 모음

## 📋 개요

본 문서는 법률 AI 어시스턴트 시스템의 주요 아키텍처와 데이터 플로우를 시각적으로 표현한 다이어그램들을 정리한 문서입니다.

---

## 🏗️ 전체 시스템 아키텍처 다이어그램

### 1. 컴포넌트 구조도

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Streamlit App<br/>main.py] --> B[Document Search Tab]
        A --> C[Document Analysis Tab]
        A --> D[Legal Q&A Tab]
        A --> E[System Status Tab]
    end

    subgraph "Workflow Layer - LangGraph"
        F[Legal Workflow<br/>legal_workflow.py] --> G[Retrieval Node<br/>retrieval.py]
        F --> H[Analysis Node<br/>analysis.py]
        
        G --> I[PostgreSQL Search]
        G --> J[Vector Search]
        G --> K[Hybrid Results]
        G --> L[Reranking]
        
        H --> M[Summary Extraction]
        H --> N[Key Points]
        H --> O[Legal Issues]
        H --> P[Entity Extraction]
        H --> Q[Risk Assessment]
    end

    subgraph "State Management"
        R[LegalWorkflowState<br/>legal_workflow_state.py]
        S[RetrievalState]
        T[AnalysisState]
    end

    subgraph "Core Services"
        U[SQLite Manager<br/>sqlite.py] --> V[(SQLite DB)]
        W[Vector Store Manager<br/>vector_store.py] --> X[(ChromaDB)]
        Y[OpenAI Client<br/>openai_client.py]
        Z[Clova Client<br/>clova_client.py]
        AA[KURE Embeddings<br/>kure_embeddings.py]
    end

    subgraph "Data Models"
        BB[Legal Document<br/>simple_models.py]
        CC[Legal Document ORM]
    end

    %% Connections
    A --> F
    F --> R
    G --> S
    H --> T
    
    G --> U
    G --> W
    H --> Y
    H --> Z
    W --> AA
    
    U --> BB
    U --> CC
    
    I --> V
    J --> X
```

### 2. 시퀀스 다이어그램 - 사용자 요청 처리 흐름

```mermaid
sequenceDiagram
    participant User as 사용자
    participant App as Streamlit App
    participant WF as Legal Workflow
    participant RN as Retrieval Node
    participant AN as Analysis Node
    participant DB as SQLite DB
    participant VS as Vector Store
    participant LLM as LLM Client
    participant EMB as Embeddings

    User->>App: 문서 검색 요청
    App->>WF: 워크플로우 시작
    WF->>RN: 검색 노드 실행
    
    par PostgreSQL Search
        RN->>DB: SQL 검색 실행
        DB-->>RN: 검색 결과 반환
    and Vector Search
        RN->>EMB: 쿼리 임베딩 생성
        EMB-->>RN: 임베딩 벡터
        RN->>VS: 벡터 유사도 검색
        VS-->>RN: 벡터 검색 결과
    end
    
    RN->>RN: 결과 하이브리드 조합
    RN->>RN: 리랭킹 수행
    RN-->>WF: 검색 완료
    
    WF->>AN: 분석 노드 실행
    AN->>LLM: 문서 분석 요청
    LLM-->>AN: 분석 결과
    AN-->>WF: 분석 완료
    
    WF-->>App: 워크플로우 완료
    App-->>User: 결과 표시
```

### 3. 데이터 플로우 다이어그램

```mermaid
graph LR
    subgraph "Data Flow"
        A[User Query] --> B[Retrieval Workflow]
        B --> C[PostgreSQL Search]
        B --> D[Vector Search]
        C --> E[Hybrid Combination]
        D --> E
        E --> F[Reranking]
        F --> G[Retrieved Documents]
        G --> H[Analysis Workflow]
        H --> I[Document Analysis]
        I --> J[Final Results]
    end

    subgraph "State Transitions"
        K[Initial State] --> L[Retrieval State]
        L --> M[Analysis State]
        M --> N[Final State]
    end

    subgraph "Error Handling"
        O[Error Occurred] --> P[Error Handler]
        P --> Q[Error State]
    end

    %% Flow connections
    B -.-> L
    H -.-> M
    J -.-> N
    
    %% Error flows
    B -.-> O
    H -.-> O
```

---

## 🔄 LangGraph 워크플로우 상세 다이어그램

### 1. 검색 워크플로우 (Retrieval Workflow)

```mermaid
graph TD
    A[시작: 사용자 쿼리] --> B[PostgreSQL 검색]
    B --> C[벡터 검색]
    C --> D[결과 하이브리드 조합]
    D --> E[BGE 리랭킹]
    E --> F[최종 결과 포맷팅]
    F --> G[검색 완료]
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
    style E fill:#fff3e0
```

### 2. 분석 워크플로우 (Analysis Workflow)

```mermaid
graph TD
    A[시작: 문서 내용] --> B[문서 요약]
    B --> C[핵심 포인트 추출]
    C --> D[법적 쟁점 식별]
    D --> E[개체명 인식]
    E --> F[권고사항 생성]
    F --> G[위험도 평가]
    G --> H[결과 통합]
    H --> I[분석 완료]
    
    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style D fill:#ffebee
    style G fill:#fff3e0
```

### 3. 조건부 워크플로우

```mermaid
graph TD
    A[워크플로우 시작] --> B[검색 실행]
    B --> C{검색 성공?}
    C -->|예| D[분석 실행]
    C -->|아니오| E[오류 처리]
    D --> F{분석 성공?}
    F -->|예| G[결과 반환]
    F -->|아니오| E
    E --> H[오류 메시지 반환]
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
    style H fill:#ffcdd2
    style E fill:#fff3e0
```

---

## 🗄️ 데이터베이스 아키텍처

### 1. 데이터 저장소 구조

```mermaid
graph TB
    subgraph "SQLite Database"
        A[legal_documents 테이블]
        A --> A1[id: INTEGER]
        A --> A2[title: TEXT]
        A --> A3[content: TEXT]
        A --> A4[document_type: TEXT]
        A --> A5[category: TEXT]
        A --> A6[source: TEXT]
        A --> A7[metadata: JSON]
    end
    
    subgraph "ChromaDB Vector Store"
        B[legal_documents 컬렉션]
        B --> B1[document_id: STRING]
        B --> B2[content: TEXT]
        B --> B3[embedding: VECTOR]
        B --> B4[metadata: DICT]
    end
    
    subgraph "KURE Embeddings"
        C[한국어 임베딩 모델]
        C --> C1[차원: 768]
        C --> C2[모델: sentence-transformers]
    end
    
    A -.-> |문서 ID| B
    C --> |임베딩 생성| B
```

### 2. 검색 프로세스

```mermaid
graph LR
    A[사용자 쿼리] --> B[쿼리 전처리]
    B --> C[PostgreSQL 검색]
    B --> D[임베딩 생성]
    D --> E[벡터 검색]
    
    C --> F[결과 1: SQL 매칭]
    E --> G[결과 2: 의미적 유사도]
    
    F --> H[하이브리드 조합]
    G --> H
    H --> I[BGE 리랭킹]
    I --> J[최종 결과]
    
    style A fill:#e1f5fe
    style J fill:#c8e6c9
    style I fill:#fff3e0
```

---

## 🧠 LLM 클라이언트 아키텍처

### 1. Multi-LLM 지원 구조

```mermaid
graph TD
    A[사용자 요청] --> B[LLM 프로바이더 선택]
    B --> C{Clova 사용 가능?}
    C -->|예| D[HyperClova-X 클라이언트]
    C -->|아니오| E[OpenAI GPT-4o 클라이언트]
    
    D --> F[API 호출]
    E --> F
    F --> G[응답 처리]
    G --> H[결과 반환]
    
    subgraph "공통 인터페이스"
        I[chat_completion]
        J[analyze_legal_document]
        K[answer_legal_question]
        L[summarize_text]
        M[extract_key_points]
    end
    
    D --> I
    E --> I
    
    style C fill:#fff3e0
    style H fill:#c8e6c9
```

### 2. 프롬프트 처리 흐름

```mermaid
graph LR
    A[사용자 입력] --> B[시스템 프롬프트 생성]
    B --> C[메시지 구조화]
    C --> D[LLM API 호출]
    D --> E[응답 수신]
    E --> F[후처리]
    F --> G[구조화된 결과]
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
    style B fill:#fff3e0
```

---

## 🎨 Streamlit UI 아키텍처

### 1. 앱 구조

```mermaid
graph TD
    A[main.py] --> B[세션 상태 초기화]
    B --> C[헤더 표시]
    C --> D[사이드바 설정]
    D --> E[탭 구성]
    
    E --> F[문서 검색 탭]
    E --> G[문서 분석 탭]
    E --> H[법률 Q&A 탭]
    E --> I[시스템 현황 탭]
    
    F --> J[검색 인터페이스]
    F --> K[결과 표시]
    
    G --> L[분석 인터페이스]
    G --> M[분석 결과 표시]
    
    style A fill:#e1f5fe
    style J fill:#fff3e0
    style L fill:#fff3e0
```

### 2. 상태 관리

```mermaid
graph LR
    A[사용자 상호작용] --> B[세션 상태 업데이트]
    B --> C[search_results]
    B --> D[analysis_result]
    B --> E[selected_document]
    
    C --> F[UI 업데이트]
    D --> F
    E --> F
    
    F --> G[사용자에게 표시]
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
```

---

## ⚡ 성능 및 확장성 다이어그램

### 1. 현재 성능 병목점

```mermaid
graph TD
    A[사용자 요청] --> B[Streamlit 처리]
    B --> C[LangGraph 워크플로우]
    C --> D[검색 노드]
    D --> E[PostgreSQL 쿼리]
    D --> F[벡터 검색]
    C --> G[분석 노드]
    G --> H[LLM API 호출]
    
    E -.-> |병목 1| I[SQL 검색 속도]
    F -.-> |병목 2| J[임베딩 생성 시간]
    H -.-> |병목 3| K[LLM 응답 지연]
    
    style I fill:#ffcdd2
    style J fill:#ffcdd2
    style K fill:#ffcdd2
```

### 2. 최적화된 아키텍처 (Future)

```mermaid
graph TD
    A[사용자 요청] --> B[로드 밸런서]
    B --> C[캐시 레이어]
    C --> D{캐시 히트?}
    D -->|예| E[캐시된 결과 반환]
    D -->|아니오| F[워크플로우 실행]
    
    F --> G[병렬 검색]
    G --> H[PostgreSQL 검색]
    G --> I[벡터 검색]
    
    H --> J[결과 조합]
    I --> J
    J --> K[분석 처리]
    K --> L[결과 캐싱]
    L --> M[사용자에게 반환]
    
    style E fill:#c8e6c9
    style C fill:#fff3e0
    style G fill:#e1f5fe
```

---

## 🔐 보안 아키텍처

### 1. 보안 계층

```mermaid
graph TD
    A[사용자 요청] --> B[입력 검증]
    B --> C[인증/인가]
    C --> D[API 키 관리]
    D --> E[데이터 암호화]
    E --> F[로깅 및 모니터링]
    F --> G[응답 반환]
    
    style B fill:#fff3e0
    style C fill:#fff3e0
    style D fill:#ffcdd2
    style E fill:#ffcdd2
```

### 2. 데이터 보호

```mermaid
graph LR
    A[민감 데이터] --> B[암호화]
    B --> C[안전한 저장소]
    C --> D[접근 제어]
    D --> E[감사 로그]
    
    style A fill:#ffcdd2
    style C fill:#c8e6c9
    style E fill:#fff3e0
```

---

## 📊 모니터링 및 로깅

### 1. 모니터링 아키텍처

```mermaid
graph TD
    A[시스템 컴포넌트] --> B[메트릭 수집]
    B --> C[로그 집계]
    C --> D[대시보드 표시]
    D --> E[알림 시스템]
    
    A --> F[성능 지표]
    A --> G[오류 추적]
    A --> H[사용량 통계]
    
    F --> B
    G --> B
    H --> B
    
    style D fill:#c8e6c9
    style E fill:#fff3e0
```

### 2. 로그 플로우

```mermaid
graph LR
    A[애플리케이션 로그] --> B[구조화된 로깅]
    B --> C[로그 파일]
    C --> D[로그 분석]
    D --> E[인사이트 추출]
    
    style B fill:#e1f5fe
    style E fill:#c8e6c9
```

---

## 📋 결론

본 다이어그램 모음은 법률 AI 어시스턴트 시스템의 전체적인 구조와 데이터 흐름을 시각적으로 표현하여 시스템 이해도를 높이고, 향후 개발 및 유지보수에 참고할 수 있는 자료로 활용할 수 있습니다.

각 다이어그램은 시스템의 다른 관점에서의 구조를 보여주며, 전체적인 아키텍처 설계의 일관성과 각 컴포넌트 간의 관계를 명확히 보여줍니다.

---

**작성자**: AI Assistant  
**작성일**: 2024년 12월 26일 