# Palm Mind AI — RAG Backend

A modular, API-based Retrieval-Augmented Generation (RAG) backend built with **FastAPI, Google Gemini, Qdrant, PostgreSQL, and Redis**.

The application allows users to upload PDF and TXT documents, retrieve relevant information through semantic search, and have contextual multi-turn conversations with an AI assistant. It also supports interview booking through conversational information extraction and explicit user confirmation.

## Key Features

### 1. Document Ingestion
- Upload PDF and TXT documents through a REST API.
- Extract text while preserving filename and page information.
- Support two selectable chunking strategies:
  - **Fixed chunking**
  - **Recursive chunking**
- Generate document embeddings using Google's Gemini embedding model.
- Store document vectors and metadata in Qdrant.
- Store document-level metadata in PostgreSQL.
- Enforce a 10 MB upload size limit.

### 2. Conversational RAG
- Custom RAG pipeline implemented without using a prebuilt `RetrievalQAChain`.
- Semantic retrieval using Qdrant.
- Context-aware question rewriting for follow-up questions.
- Retrieve relevant document chunks before generating responses.
- Construct prompts using retrieved context and conversation history.
- Provide grounded responses based on uploaded documents.

### 3. Conversation Memory
- Redis-based conversation history.
- Maintain context across multiple messages using session IDs.
- Limit stored conversation history and configure expiration.
- Support multi-turn conversations.

### 4. Interview Booking
- Extract interview booking details from natural language conversations.
- Identify the candidate's name, email, interview date, and time.
- Ask for missing information when necessary.
- Require explicit user confirmation before saving a booking.
- Persist confirmed bookings in PostgreSQL.

## Technology Stack

| Component | Technology |
|---|---|
| Backend Framework | FastAPI |
| Programming Language | Python |
| LLM | Google Gemini |
| Embedding Model | Gemini Embedding |
| Vector Database | Qdrant |
| Relational Database | PostgreSQL |
| Conversation Memory | Redis |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Document Processing | PyPDF |
| Chunking | LangChain Text Splitters |
| Testing | Pytest |
| Infrastructure | Docker Compose |

## Architecture

```text
                    Client
                      |
                      v
                 FastAPI API
                  /       \
                 /         \
                v           v
       Document API    Conversation API
            |                 |
            v                 v
    Document Processor   Booking Workflow
            |                 |
            v                 v
       Chunking          Gemini Extraction
            |                 |
            v                 v
       Embeddings        PostgreSQL
            |
            v
          Qdrant


Conversation API
       |
       v
  RAG Service
       |
       +------> Question Rewriter
       |
       +------> Retrieval Service ------> Qdrant
       |
       +------> Prompt Service
       |
       +------> Gemini LLM
       |
       +------> Redis Conversation Memory
```

### Storage Responsibilities

- **Qdrant:** Stores document chunk vectors and their associated payload metadata.
- **PostgreSQL:** Stores document records and confirmed interview bookings.
- **Redis:** Stores conversational history associated with session IDs.

## Project Structure

```text
Palm Mind Assessment/
│
├── app/
│   ├── api/
│   │   ├── conversation.py
│   │   └── documents.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── redis.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   ├── models.py
│   │   └── session.py
│   │
│   ├── repositories/
│   │   ├── booking_repository.py
│   │   └── document_repository.py
│   │
│   ├── schemas/
│   │   ├── booking.py
│   │   ├── conversation.py
│   │   ├── document.py
│   │   └── retrieval.py
│   │
│   ├── services/
│   │   ├── booking_extraction_service.py
│   │   ├── booking_workflow_service.py
│   │   ├── chat_memory_service.py
│   │   ├── chunking.py
│   │   ├── document_processor.py
│   │   ├── embedding_service.py
│   │   ├── llm_service.py
│   │   ├── prompt_service.py
│   │   ├── qdrant_service.py
│   │   ├── question_rewriter.py
│   │   ├── rag_service.py
│   │   └── retrieval_service.py
│   │
│   └── main.py
│
├── migrations/
├── scripts/
├── tests/
├── docker-compose.yml
├── alembic.ini
├── .env.example
├── .gitignore
└── requirements.txt
```

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python
- Git
- Docker Desktop
- PostgreSQL
- Google Gemini API key

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_DIRECTORY>
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your local `.env` file using the example:

```powershell
Copy-Item .env.example .env
```

Configure the required environment variables in `.env`, including:

- PostgreSQL connection URL
- Redis connection URL
- Qdrant connection URL
- Google Gemini API key
- Embedding model configuration
- Embedding dimensions
- Qdrant collection name
- LLM model configuration

**Never commit your `.env` file or expose API keys and database credentials.**

### 5. Start Redis and Qdrant

Start the infrastructure services using Docker Compose:

```bash
docker compose up -d
```

Verify the containers:

```bash
docker compose ps
```

The application uses PostgreSQL separately. Make sure your PostgreSQL server is running and the configured database exists.

### 6. Run Database Migrations

```bash
alembic upgrade head
```

This creates the required database tables.

### 7. Start the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

**GET** `/health`

Checks the application's health endpoint.

Example response:

```json
{
  "status": "healthy"
}
```

### Document Upload

**POST** `/documents/upload`

Uploads and processes a PDF or TXT document.

Content type: `multipart/form-data`

Parameters:

| Parameter | Type | Description |
|---|---|---|
| `file` | File | PDF or TXT document |
| `strategy` | String | Chunking strategy: `fixed` or `recursive` |

Example using cURL:

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload" \
  -F "file=@document.pdf" \
  -F "strategy=recursive"
```

Example response:

```json
{
  "document_uuid": "generated-document-uuid",
  "filename": "document.pdf",
  "pages_extracted": 3,
  "chunks_created": 18,
  "vectors_stored": 18,
  "chunking_strategy": "recursive"
}
```

### Conversational RAG

**POST** `/conversation/chat`

Sends a message to the conversational RAG system.

Example request:

```json
{
  "session_id": "user-session-001",
  "message": "What information is available in the uploaded document?"
}
```

Example response:

```json
{
  "session_id": "user-session-001",
  "answer": "The response generated using the retrieved document context."
}
```

Use the same `session_id` across messages to maintain conversational context.

## Interview Booking Workflow

The conversational assistant can identify interview booking requests and collect the required information.

The workflow follows these steps:

1. Identify whether the user intends to book an interview.
2. Extract explicitly provided booking details.
3. Ask for any missing information.
4. Present the collected details for confirmation.
5. Require the user to explicitly reply `CONFIRM`.
6. Save the confirmed booking in PostgreSQL.

The application does not save a booking merely because the required information was mentioned. Explicit confirmation is required.

## Testing

Run the complete test suite:

```bash
pytest -v
```

Run a specific test module:

```bash
pytest -v tests/test_document_api.py
```

The test suite covers document processing, chunking, API behavior, embeddings and retrieval workflows, conversation memory, RAG, and interview booking logic.

## Design Considerations

- **Modular architecture:** Separates API routes, schemas, services, repositories, and database configuration.
- **Custom RAG implementation:** Provides control over retrieval, prompt construction, question rewriting, and response generation.
- **Grounded generation:** Uses retrieved document context to reduce unsupported responses.
- **Session-based memory:** Maintains conversational context using Redis.
- **Explicit booking confirmation:** Prevents booking records from being created without user approval.
- **Data consistency:** Uses document UUIDs to associate Qdrant vectors with PostgreSQL document metadata and attempts vector cleanup if metadata persistence fails.
- **Environment-based configuration:** Keeps credentials and service configuration outside the source code.

## Scope

This project focuses on backend APIs and AI/RAG functionality. It does not include a frontend interface.

The implementation is designed as an internship technical assessment project demonstrating document ingestion, semantic retrieval, conversational AI, database integration, and modular backend development.

## Author

**Aayus Prasai**
GitHub: [github.com/prasai-ap](https://github.com/prasai-ap)
