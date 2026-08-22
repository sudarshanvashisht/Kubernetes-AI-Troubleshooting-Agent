# AI Kubernetes Troubleshooting Agent

An AI-powered system for diagnosing and troubleshooting Kubernetes clusters.

## Architecture

```
Frontend (Next.js)
    ↓
FastAPI Backend (Orchestrator)
    ↓
Kubernetes Investigation Layer
    ↓
AI Kubernetes Agent
    ↓
LLM Reasoning (OpenRouter)
    ↓
Root Cause + Suggested Fix
    ↓
Frontend Diagnosis
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Running with Docker

1. Copy environment files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

2. Start all services:

```bash
docker compose up --build
```

3. Access the application:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## Project Structure

```
ai-kubernetes-agent/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── kubernetes/   # K8s inspection layer
│   │   ├── ai/           # AI reasoning agent
│   │   ├── services/     # Business logic
│   │   └── models/       # Pydantic schemas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components
│   │   ├── services/     # API client
│   │   ├── hooks/        # Custom hooks
│   │   └── types/        # TypeScript types
│   └── Dockerfile
├── docs/                 # Documentation
├── prompts/              # AI prompt templates
├── docker-compose.yml
└── README.md
```

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend  | FastAPI, Python 3.12, Uvicorn     |
| AI       | OpenRouter (LLM gateway)          |
| Infra    | Docker, Docker Compose            |

## License

MIT
