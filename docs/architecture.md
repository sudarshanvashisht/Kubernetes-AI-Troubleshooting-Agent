# Architecture Overview

## System Flow

```
User clicks "Investigate Cluster"
        ↓
API call (POST /diagnose)
        ↓
Kubernetes investigation (kubectl data collection)
        ↓
AI reasoning (OpenRouter LLM analysis)
        ↓
Diagnosis shown to user
```

## Components

### Frontend (Next.js)
- User interface for triggering investigations
- Displays diagnosis results
- Communicates with backend via REST API

### Backend (FastAPI)
- Orchestrates the troubleshooting pipeline
- Manages Kubernetes data collection
- Interfaces with AI reasoning layer

### Kubernetes Investigation Layer
- Connects to cluster via kubeconfig
- Collects pod, deployment, event, and node data
- Formats data for AI analysis

### AI Agent
- Sends collected data to LLM via OpenRouter
- Receives root cause analysis and fix suggestions
- Formats response for frontend consumption
