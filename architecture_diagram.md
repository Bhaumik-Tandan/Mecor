# 🏗️ Mercor Search Agent - Visual Architecture

## System Architecture Diagram

```mermaid
graph TB
    %% User Interface Layer
    subgraph "User Interface"
        UI[Interview Testing Script]
        UI --> |Interactive Mode| INT[Interactive Testing]
        UI --> |Single Query| SQ[Single Query Testing]
        UI --> |Batch Mode| BM[Batch Testing]
    end

    %% Main Application Layer
    subgraph "Main Application"
        MA[Main Application<br/>main.py]
        SA[SearchAgent Class]
        MA --> SA
        SA --> |run_evaluation| SEARCH_SVC
        SA --> |save_results| RESULTS
    end

    %% Configuration Layer
    subgraph "Configuration"
        CONFIG[Settings<br/>settings.py]
        API_CONFIG[API Configuration]
        SEARCH_CONFIG[Search Parameters]
        JOB_CONFIG[Job Categories]
        CONFIG --> API_CONFIG
        CONFIG --> SEARCH_CONFIG
        CONFIG --> JOB_CONFIG
    end

    %% Service Layer
    subgraph "Services"
        SEARCH_SVC[Search Service<br/>search_service.py]
        EVAL_SVC[Evaluation Service<br/>evaluation_service.py]
        EMBED_SVC[Embedding Service<br/>embedding_service.py]
        
        SEARCH_SVC --> |vector_search| VECTOR[Vector Search]
        SEARCH_SVC --> |bm25_search| BM25[BM25 Search]
        SEARCH_SVC --> |hybrid_search| HYBRID[Hybrid Search]
        SEARCH_SVC --> |apply_filters| FILTERS[Hard/Soft Filters]
        
        EVAL_SVC --> |evaluate_candidates| EVAL_API[Mercor Evaluation API]
        EVAL_SVC --> |format_summary| FORMAT[Result Formatting]
        
        EMBED_SVC --> |get_embeddings| VOYAGE[Voyage AI]
        EMBED_SVC --> |batch_embed| BATCH[Batch Processing]
    end

    %% External APIs
    subgraph "External APIs"
        TURBO[Turbopuffer<br/>Vector Database]
        VOYAGE[Voyage AI<br/>Embeddings]
        MERCOR[Mercor API<br/>Evaluation]
    end

    %% Data Models
    subgraph "Data Models"
        CP[CandidateProfile]
        SQ_MODEL[SearchQuery]
        SR[SearchResult]
        ER[EvaluationResult]
        SS[SearchStrategy]
    end

    %% Utilities
    subgraph "Utilities"
        PT[PerformanceTimer]
        RL[Retry Logic]
        PP[Parallel Processing]
        FO[File Operations]
        LOG[Logging]
    end

    %% Results & Output
    subgraph "Results & Output"
        RESULTS[Results Management]
        JSON_OUT[JSON Results]
        CSV_OUT[CSV Summaries]
        LOGS[Log Files]
        METRICS[Performance Metrics]
        
        RESULTS --> JSON_OUT
        RESULTS --> CSV_OUT
        RESULTS --> LOGS
        RESULTS --> METRICS
    end

    %% Connections
    UI --> MA
    MA --> CONFIG
    SEARCH_SVC --> TURBO
    SEARCH_SVC --> VOYAGE
    EVAL_SVC --> MERCOR
    EMBED_SVC --> VOYAGE
    
    SEARCH_SVC --> CP
    SEARCH_SVC --> SQ_MODEL
    SEARCH_SVC --> SR
    EVAL_SVC --> ER
    SEARCH_SVC --> SS
    
    SEARCH_SVC --> PT
    SEARCH_SVC --> RL
    SEARCH_SVC --> PP
    EVAL_SVC --> PT
    EVAL_SVC --> RL
    EVAL_SVC --> LOG
    
    MA --> RESULTS
    SEARCH_SVC --> RESULTS
    EVAL_SVC --> RESULTS

    %% Styling
    classDef serviceClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef apiClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef modelClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef utilClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef configClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef resultClass fill:#f1f8e9,stroke:#33691e,stroke-width:2px

    class SEARCH_SVC,EVAL_SVC,EMBED_SVC serviceClass
    class TURBO,VOYAGE,MERCOR apiClass
    class CP,SQ_MODEL,SR,ER,SS modelClass
    class PT,RL,PP,FO,LOG utilClass
    class CONFIG,API_CONFIG,SEARCH_CONFIG,JOB_CONFIG configClass
    class RESULTS,JSON_OUT,CSV_OUT,LOGS,METRICS resultClass
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Interview Script
    participant SA as SearchAgent
    participant SS as SearchService
    participant ES as EvaluationService
    participant TP as Turbopuffer
    participant MA as Mercor API
    participant Results

    User->>UI: Enter Query
    UI->>SA: test_single_query()
    SA->>SS: search_candidates()
    
    SS->>SS: vector_search()
    SS->>TP: Query Vector Database
    TP-->>SS: Vector Results
    
    SS->>SS: bm25_search()
    SS->>TP: Query Text Database
    TP-->>SS: BM25 Results
    
    SS->>SS: hybrid_search()
    SS->>SS: apply_filters()
    SS-->>SA: Candidate Profiles
    
    SA->>ES: evaluate_candidates()
    ES->>MA: Send Candidates
    MA-->>ES: Evaluation Scores
    ES-->>SA: Evaluation Results
    
    SA->>Results: save_results()
    SA-->>UI: Formatted Results
    UI-->>User: Display Results
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph "Input Layer"
        Q[Query Input]
        C[Category]
        S[Strategy]
    end
    
    subgraph "Processing Layer"
        QE[Query Enhancement]
        VS[Vector Search]
        BS[BM25 Search]
        HS[Hybrid Search]
        HF[Hard Filters]
        SF[Soft Filters]
    end
    
    subgraph "Evaluation Layer"
        EV[Evaluation]
        SC[Score Calculation]
        RF[Result Formatting]
    end
    
    subgraph "Output Layer"
        JSON[JSON Results]
        CSV[CSV Summary]
        LOG[Logs]
        MET[Metrics]
    end
    
    Q --> QE
    C --> QE
    S --> QE
    
    QE --> VS
    QE --> BS
    VS --> HS
    BS --> HS
    HS --> HF
    HF --> SF
    
    SF --> EV
    EV --> SC
    SC --> RF
    
    RF --> JSON
    RF --> CSV
    RF --> LOG
    RF --> MET
```

## Performance Flow

```mermaid
graph TD
    subgraph "Performance Monitoring"
        PT[PerformanceTimer]
        RL[Retry Logic]
        PP[Parallel Processing]
        RM[Resource Monitoring]
    end
    
    subgraph "Search Performance"
        VS_TIME[Vector Search: 2-3s]
        BS_TIME[BM25 Search: 1-2s]
        HS_TIME[Hybrid Search: 3-5s]
    end
    
    subgraph "Evaluation Performance"
        SE_TIME[Single Eval: 2-4s]
        BE_TIME[Batch Eval: 10-20/min]
        RT_TIME[Rate Limiting]
    end
    
    subgraph "System Resources"
        MEM[Memory: 100-200MB]
        CPU[CPU: Moderate]
        NET[Network: Efficient]
    end
    
    PT --> VS_TIME
    PT --> BS_TIME
    PT --> HS_TIME
    PT --> SE_TIME
    PT --> BE_TIME
    
    RL --> RT_TIME
    PP --> CPU
    RM --> MEM
    RM --> NET
```

## Security & Reliability Architecture

```mermaid
graph TB
    subgraph "Security Layer"
        EK[Environment Keys]
        NV[No Hardcoded Values]
        SA[Secure API Calls]
    end
    
    subgraph "Error Handling"
        EH[Exception Handling]
        GD[Graceful Degradation]
        EL[Error Logging]
    end
    
    subgraph "Reliability"
        RB[Retry with Backoff]
        TO[Timeout Management]
        CP[Connection Pooling]
    end
    
    subgraph "Monitoring"
        PM[Performance Monitoring]
        RM[Resource Monitoring]
        HC[Health Checks]
    end
    
    EK --> SA
    NV --> SA
    SA --> EH
    EH --> GD
    EH --> EL
    
    GD --> RB
    RB --> TO
    TO --> CP
    
    CP --> PM
    PM --> RM
    RM --> HC
```

These diagrams provide a comprehensive visual representation of your Mercor Search Agent architecture, showing the relationships between components, data flow, performance characteristics, and security/reliability features. 