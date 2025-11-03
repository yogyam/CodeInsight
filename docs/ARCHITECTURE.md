# Architecture Overview

## System Architecture

```mermaid
graph TD
    A[GitHub PR Event] -->|Webhook| B[FastAPI Server]
    B -->|Enqueue Task| C[Redis Queue]
    C -->|Process| D[Celery Worker]
    
    D -->|1. Get PR Diff| E[GitHub API]
    D -->|2. Retrieve Context| F[RAG Service]
    D -->|3. Get User Memory| G[Memory Service]
    D -->|4. Generate Review| H[Claude Sonnet 4.5]
    
    F -->|Vector Search| I[(PostgreSQL + pgvector)]
    G -->|Query Memory| I
    
    H -->|Review Results| D
    D -->|5. Post Comments| E
    D -->|6. Store History| I
    
    B -->|Health Check| J[Monitoring]
    
    style A fill:#e1f5ff
    style H fill:#ffe1e1
    style I fill:#e1ffe1
    style C fill:#fff4e1
```

## Component Diagram

```mermaid
graph LR
    subgraph "GitHub"
        GH[GitHub Repository]
        PR[Pull Request]
    end
    
    subgraph "Application Layer"
        API[FastAPI<br/>Webhook Server]
        WORKER[Celery<br/>Worker]
    end
    
    subgraph "Service Layer"
        GITHUB[GitHub Service]
        LLM[LLM Service]
        MEM[Memory Service]
        RAG[RAG Service]
        EMB[Embedding Service]
    end
    
    subgraph "Data Layer"
        REDIS[(Redis)]
        POSTGRES[(PostgreSQL<br/>+ pgvector)]
    end
    
    subgraph "External APIs"
        ANTHROPIC[Claude API]
        GHAPI[GitHub API]
    end
    
    PR -->|webhook| API
    API -->|queue| REDIS
    REDIS -->|consume| WORKER
    
    WORKER --> GITHUB
    WORKER --> LLM
    WORKER --> MEM
    WORKER --> RAG
    
    GITHUB --> GHAPI
    LLM --> ANTHROPIC
    
    MEM --> POSTGRES
    RAG --> EMB
    EMB --> POSTGRES
    
    style API fill:#4CAF50
    style WORKER fill:#2196F3
    style POSTGRES fill:#9C27B0
    style REDIS fill:#FF5722
```

## Data Flow - PR Review Process

```mermaid
sequenceDiagram
    participant GH as GitHub
    participant API as FastAPI
    participant Q as Redis Queue
    participant W as Celery Worker
    participant DB as PostgreSQL
    participant LLM as Claude
    
    GH->>API: PR opened webhook
    API->>API: Verify signature
    API->>Q: Enqueue review task
    API->>GH: 200 OK
    
    Q->>W: Process task
    W->>GH: Fetch PR diff
    GH->>W: Return diff
    
    W->>DB: Search similar code
    DB->>W: Return context
    
    W->>DB: Get user memory
    DB->>W: Return preferences
    
    W->>LLM: Generate review
    Note over W,LLM: Send: diff + context + memory
    LLM->>W: Return review
    
    W->>GH: Post review comments
    W->>DB: Store review history
    W->>Q: Task complete
```

## Database Schema

```mermaid
erDiagram
    USER_MEMORY {
        int id PK
        string user_id
        string repository_id
        string memory_type
        text content
        jsonb metadata
        vector embedding
        timestamp created_at
        timestamp updated_at
    }
    
    CODE_EMBEDDINGS {
        int id PK
        string repository_id
        text file_path
        text code_chunk
        vector embedding
        jsonb metadata
        timestamp created_at
    }
    
    PR_REVIEWS {
        int id PK
        int pr_number
        string repository_id
        string user_id
        text review_content
        int comments_count
        timestamp created_at
    }
    
    USER_MEMORY ||--o{ PR_REVIEWS : "has"
    CODE_EMBEDDINGS ||--o{ PR_REVIEWS : "informs"
```

## Deployment Architecture

### Render Deployment

```mermaid
graph TB
    subgraph "Render"
        WEB[Web Service<br/>FastAPI]
        WORKER[Background Worker<br/>Celery]
        REDIS[Redis Service]
        
        subgraph "Supabase"
            DB[(PostgreSQL<br/>+ pgvector)]
        end
    end
    
    subgraph "External"
        GH[GitHub]
        CLAUDE[Claude API]
    end
    
    GH -->|webhook| WEB
    WEB -->|queue| REDIS
    REDIS -->|tasks| WORKER
    
    WEB --> DB
    WORKER --> DB
    WORKER --> GH
    WORKER --> CLAUDE
    
    style WEB fill:#4CAF50
    style WORKER fill:#2196F3
    style DB fill:#9C27B0
    style REDIS fill:#FF5722
```

## Key Components

### 1. FastAPI Webhook Server (`app/main.py`)
- Receives GitHub webhook events
- Validates webhook signatures
- Enqueues tasks to Celery
- Provides health check endpoints

### 2. Celery Worker (`app/tasks.py`)
- Processes PR review tasks asynchronously
- Orchestrates review pipeline
- Handles retries on failures
- Manages background indexing

### 3. GitHub Service (`app/github_service.py`)
- GitHub API client wrapper
- Fetches PR diffs and metadata
- Posts review comments
- Manages authentication

### 4. LLM Service (`app/llm_service.py`)
- Claude API integration
- Generates code reviews
- Formats review responses
- Handles API errors

### 5. Memory Service (`app/memory_service.py`)
- User preference storage
- Review history tracking
- Learning from feedback
- Context retrieval

### 6. RAG Service (`app/rag_service.py`)
- Code indexing
- Semantic search
- Context building
- Related file detection

### 7. Embedding Service (`app/embedding_service.py`)
- Vector embedding generation
- Similarity search
- Batch processing
- Model management

### 8. Database Layer (`app/database.py`)
- SQLAlchemy models
- Connection management
- Session handling
- pgvector integration

## Security Architecture

```mermaid
graph TD
    A[GitHub Webhook] -->|HMAC SHA-256| B{Signature<br/>Verification}
    B -->|Valid| C[Process Request]
    B -->|Invalid| D[Reject 401]
    
    E[GitHub API Calls] -->|JWT| F{App Auth}
    F -->|Valid Token| G[API Access]
    F -->|Invalid| H[Auth Error]
    
    I[Sensitive Data] -->|Environment Vars| J[Encrypted Storage]
    I -->|Private Key| K[Secure File]
    
    style B fill:#FFD700
    style F fill:#FFD700
    style J fill:#90EE90
    style K fill:#90EE90
```

## Performance Considerations

### Scaling Strategies

1. **Horizontal Scaling**
   - Multiple FastAPI instances behind load balancer
   - Multiple Celery workers for parallel processing
   - Redis cluster for high availability

2. **Caching**
   - Cache GitHub API responses
   - Cache LLM responses for similar code
   - Cache embeddings for frequently accessed code

3. **Optimization**
   - Limit file size for reviews
   - Batch embedding generation
   - Index only relevant code files
   - Use connection pooling

### Resource Requirements

| Component | CPU | Memory | Notes |
|-----------|-----|--------|-------|
| FastAPI | 0.5 CPU | 512 MB | Can scale horizontally |
| Celery Worker | 1 CPU | 1 GB | CPU-intensive for embeddings |
| Redis | 0.25 CPU | 256 MB | Memory-based cache |
| PostgreSQL | 0.5 CPU | 1 GB | Storage for vectors |

## Future Enhancements

### Phase 2 (v1.1)
- Multi-model support (OpenAI, Gemini)
- Advanced caching layer
- Analytics dashboard
- Custom review templates

### Phase 3 (v2.0)
- Real-time conversation threads
- Organization-level insights
- Integration with CI/CD
- Custom rules engine
