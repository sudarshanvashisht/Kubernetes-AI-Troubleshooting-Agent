<div align="center">

# ☸️🤖 Kubernetes AI Troubleshooting Agent

**An autonomous AI Site Reliability Engineer that investigates your Kubernetes cluster, correlates the evidence, and hands you a root-cause diagnosis with copy-paste-ready `kubectl` fixes.**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-kubectl-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-8A2BE2)](https://openrouter.ai/)
[![InsForge](https://img.shields.io/badge/Backend%20Services-InsForge-1f6feb)](https://insforge.dev/)
[![Docker](https://img.shields.io/badge/Deploy-Docker%20Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Unspecified-lightgrey)](#-license)

</div>

---

## 📖 Table of Contents

- [What Is This?](#-what-is-this)
- [Key Features](#-key-features)
- [Console Screenshots](#-console-screenshots)
- [How It Works](#-how-it-works)
- [High-Level Architecture](#️-high-level-architecture)
- [End-to-End Workflow](#-end-to-end-workflow)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Supported Kubernetes Failures](#️-supported-kubernetes-failures)
- [Quick Start](#-quick-start)
- [Configuration Reference](#-configuration-reference)
- [Try It Yourself — Test Scenarios](#-try-it-yourself--test-scenarios)
- [API Reference](#-api-reference)
- [Security & Hardening Notes](#-security--hardening-notes)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧠 What Is This?

Debugging a broken Kubernetes cluster usually means the same tedious ritual: `kubectl get pods`, `kubectl describe pod`, `kubectl logs`, `kubectl get events`, cross-referencing deployment specs, checking service selectors — then mentally stitching it all together to figure out *why* something broke.

**Kubernetes AI Troubleshooting Agent** automates that ritual. Point it at any `kubeconfig` context, click **Investigate Cluster**, and it will:

1. Interrogate your cluster (pods, logs, events, deployments, services) exactly like an SRE would,
2. Hand the structured evidence to a Large Language Model acting as a **Senior Kubernetes SRE persona**,
3. Return a root-cause diagnosis, a plain-English explanation, ready-to-run `kubectl` remediation commands, prevention guidance, and a confidence score — all in real time, with a live progress checklist streamed to the UI.

It's built as a full-stack reference implementation: a **FastAPI** investigation/reasoning backend, a **Next.js 16 / React 19** console, **InsForge** for auth/realtime/hosting, and **OpenRouter** as a model-agnostic LLM gateway (Claude, GPT, Gemini, DeepSeek, etc.).

---

## 🚀 Key Features

| | Feature | Description |
|---|---|---|
| ☸️ | **Multi-Cluster Selector** | Dynamically reads and lists every context from your local `kubeconfig` — switch clusters from a dropdown, no restarts needed. |
| 🧭 | **Namespace Scoping** | Optionally scope an investigation to a single namespace instead of scanning the whole cluster. |
| ⏱️ | **Real-Time Pipeline Progress** | Streams a step-by-step diagnostic checklist (`✓ Checking Pods`, `✓ Reading Logs`, `✓ Analyzing Events` …) to the browser over an InsForge Socket.IO realtime channel. |
| 🕵️ | **Five-Stage Evidence Collection** | Purpose-built inspectors for pods, logs, events, deployments, and networking/services — each fails independently and gracefully, so one broken signal never blocks the pipeline. |
| 🤖 | **LLM-Powered Root Cause Analysis** | Correlates pod status, restart counts, container logs, Warning events, deployment rollout health, and service/selector mismatches to identify the *actual* underlying problem, not just a log summary. |
| 📋 | **Actionable Remediation** | Produces copy-ready `kubectl` commands and plain-English fix + prevention guidance, structured as strict JSON for reliable rendering. |
| 📊 | **Confidence Scoring** | Every diagnosis ships with a 0–100% confidence score and the reasoning behind it, so you know how much to trust the verdict. |
| 🗂️ | **Investigation History** | Past investigations are persisted (via InsForge) and browsable, complete with confidence badges and timestamps. |
| 🔒 | **Authenticated Console** | Email/password auth (with email verification) gates access to the dashboard via InsForge Auth. |
| 🔌 | **Model-Agnostic Reasoning** | Swap the underlying LLM (Claude, GPT-4, Gemini, DeepSeek, and more) with a single environment variable via OpenRouter — no code changes. |
| 🐳 | **One-Command Deployment** | Fully containerized with Docker Compose — backend, frontend, and networking wired up out of the box. |

---

## 📸 Console Screenshots

### 1. Simulated Kubernetes Failure
A broken pod (`ErrImagePull`) is deployed to the cluster as a realistic failure scenario for the agent to diagnose.

![Simulated Kubernetes Failure](./docs/assets/01-k8s-failure.png)

### 2. Cluster Selector & Diagnostic Pipeline
The authenticated dashboard lets you pick a target cluster context and namespace, then kicks off the live diagnostic pipeline.

![SRE Dashboard Cluster Selector](./docs/assets/02-dashboard-cluster.png)

### 3. Diagnosis Report & Detailed Analysis
The AI SRE returns a root cause, a detailed evidence-correlated explanation, and a confidence score.

![Root Cause & Detailed Analysis](./docs/assets/03-diagnosis-report.png)

### 4. Actionable, Copyable Remediation Commands
Ready-to-run `kubectl` commands and prevention recommendations, generated specifically for the diagnosed issue.

![Copyable Kubectl Remediation Commands](./docs/assets/04-kubectl-commands.png)

### 5. Incident History & Prevention Guidance
Every investigation is saved to history for later review, alongside prevention best practices.

![Incident History & Prevention Guidelines](./docs/assets/05-prevention-history.png)

---

## ⚙️ How It Works

At its core, the agent is a **5-step evidence pipeline** feeding a **structured LLM reasoning step**:

```
 1. Check Pods           → CrashLoopBackOff / Pending / Error detection
 2. Read Logs            → Pull logs only from problematic pods
 3. Analyze Events       → Surface Warning events (scheduling, image pulls, probes)
 4. Inspect Deployments  → Rollout health, replica availability, conditions
 5. Check Networking     → Service selectors, endpoints, ClusterIP/DNS issues
          │
          ▼
 AI SRE Reasoning (OpenRouter LLM) → strict JSON diagnosis
```

Each stage is implemented as an independent, self-healing module under `backend/app/kubernetes/` — if one stage fails (e.g. no permissions to read events), it degrades gracefully and reports an error inline rather than crashing the whole investigation.

---

## 🏗️ High-Level Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                      │
│         Pods | Deployments | Services | Events | Logs      │
│         This is where failures happen and evidence exists  │
└────────────────────────────────────────────────────────────┘
                              │  kubectl / Kubernetes API
                              ▼
┌────────────────────────────────────────────────────────────┐
│                   Investigation Layer                      │
│  1. Pod Inspector        – health, CrashLoopBackOff,        │
│                             Pending/Error states             │
│  2. Logs Collector       – container error extraction        │
│  3. Events Analyzer      – scheduling / image-pull failures  │
│  4. Deployment Inspector – rollout health verification        │
│  5. Network Inspector    – service selectors, DNS/networking │
└────────────────────────────────────────────────────────────┘
                              │  Structured Investigation Data
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    AI Kubernetes Agent                      │
│  1. Prompt Builder      – investigation data → LLM prompt    │
│  2. LLM Reasoning Layer – OpenRouter (Claude / GPT / Gemini /│
│                            DeepSeek, etc.)                    │
│  3. Root Cause Analyzer – correlates signals                 │
│  4. Fix Recommendation Engine – kubectl + YAML suggestions    │
│  5. Confidence Scoring  – diagnosis confidence %              │
└────────────────────────────────────────────────────────────┘
                              │  Investigation Result
                              ▼
┌────────────────────────────────────────────────────────────┐
│                     InsForge Backend                        │
│  – Authentication (email/password + verification)            │
│  – Realtime Socket.IO progress channel                       │
│  – Investigation history persistence                         │
└────────────────────────────────────────────────────────────┘
                              │  API Response
                              ▼
┌────────────────────────────────────────────────────────────┐
│                   Frontend Dashboard (Next.js)               │
│  – Trigger investigations   – Show live progress checklist   │
│  – Render root cause + fix  – Browse investigation history   │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 End-to-End Workflow

```text
User clicks "Investigate Cluster"
                │
                ▼
Frontend (Next.js) sends POST /investigate
                │
                ▼
FastAPI Backend (Orchestration Layer)
                │
                ├── InsForge Auth gate (frontend-side)
                ▼
Investigation Layer  ──►  emits realtime progress per step
                │
                ├── Check Pods
                ├── Read Logs
                ├── Analyze Events
                ├── Inspect Deployments
                └── Check Networking
                │
                ▼
AI Kubernetes Agent  →  Prompt Builder  →  OpenRouter LLM
                │
                ▼
Strict-JSON Root Cause Analysis + Fix + Confidence
                │
                ├── Emit "AI Reasoning" / "Diagnosis complete" (InsForge Realtime)
                │
                ▼
Frontend receives FullDiagnosisResponse
                │
                ▼
User sees: Root Cause • Explanation • Fix • kubectl commands
           • Prevention tips • Confidence % • saved to History
```

---

## 🧰 Tech Stack

<table>
<tr><td valign="top">

**Backend**
- FastAPI 0.115 + Uvicorn (async ASGI)
- Pydantic v2 / `pydantic-settings`
- `httpx` (async OpenRouter client)
- `python-socketio` + `aiohttp` (InsForge Realtime)
- Loguru structured logging
- `kubectl` CLI (v1.31.0) shelled out via `asyncio.subprocess`

</td><td valign="top">

**Frontend**
- Next.js 16 (App Router)
- React 19
- TypeScript
- Tailwind CSS v4
- `@insforge/sdk` (auth + realtime)
- Axios

</td><td valign="top">

**Platform / Infra**
- InsForge (auth, realtime, history, hosting)
- OpenRouter (LLM gateway — Claude, GPT, Gemini, DeepSeek, etc.)
- Docker & Docker Compose
- Kind / Minikube for local test clusters

</td></tr>
</table>

---

## 📁 Project Structure

```text
Kubernetes-AI-Troubleshooting-Agent/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── agent.py            # Orchestrates prompt → LLM → parsed diagnosis
│   │   │   ├── prompt_builder.py   # Builds the SRE system/user prompts
│   │   │   └── llm_client.py       # Async OpenRouter chat-completions client
│   │   ├── api/
│   │   │   ├── clusters.py         # GET /clusters — kubeconfig contexts
│   │   │   ├── investigation.py    # POST /investigate — main pipeline entrypoint
│   │   │   └── health.py           # GET /health
│   │   ├── kubernetes/
│   │   │   ├── kubectl.py          # Safe async kubectl executor + kind-cluster retry
│   │   │   ├── inspector.py        # Pod inspector
│   │   │   ├── logs_collector.py   # Log extraction for problem pods
│   │   │   ├── events_analyzer.py  # Warning event correlation
│   │   │   ├── deployment_inspector.py
│   │   │   └── network_inspector.py
│   │   ├── services/
│   │   │   ├── investigation.py    # 5-step investigation pipeline orchestrator
│   │   │   ├── diagnosis.py        # Investigation + AI diagnosis orchestrator
│   │   │   └── realtime.py         # InsForge Socket.IO progress emitter
│   │   ├── models/schemas.py       # Pydantic request/response models
│   │   ├── core/config.py          # Environment-driven settings
│   │   └── main.py                 # FastAPI app factory
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js App Router pages (dashboard, auth)
│   │   ├── services/api.ts         # Axios client for backend endpoints
│   │   ├── hooks/useAuth.ts        # InsForge auth hook (sign in/up/out, verify)
│   │   └── types/index.ts          # Shared TypeScript types
│   ├── package.json
│   └── Dockerfile
├── k8s-test-scenarios/             # Ready-made broken manifests for demos
│   ├── 01-crashloop-missing-env.yaml
│   ├── 02-imagepull-invalid-tag.yaml
│   ├── 03-oom-memory-limit.yaml
│   └── 04-service-selector-mismatch.yaml
├── docs/
│   ├── architecture.md
│   └── assets/                     # Console screenshots
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Supported Kubernetes Failures

The agent is trained (via prompt design and evidence correlation) to identify, explain, and remediate:

- `CrashLoopBackOff`
- `ImagePullBackOff` / `ErrImagePull`
- `OOMKilled` (Exit Code 137)
- Pending pods / scheduling bottlenecks
- Resource exhaustion (CPU/memory limits)
- Deployment rollout failures
- Service selector mismatches
- DNS resolution problems
- Readiness/Liveness probe failures
- Networking & Ingress configuration issues

---

## ⚡ Quick Start

### Prerequisites

- Docker & Docker Compose
- A running Kubernetes cluster (e.g. [Kind](https://kind.sigs.k8s.io/) or [Minikube](https://minikube.sigs.k8s.io/)) with a valid `kubeconfig`
- An [OpenRouter](https://openrouter.ai/) API key

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/Kubernetes-AI-Troubleshooting-Agent.git
cd Kubernetes-AI-Troubleshooting-Agent
```

### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-...            # your OpenRouter API key
OPENROUTER_MODEL=google/gemini-2.0-flash-001   # or anthropic/claude-3.5-sonnet, openai/gpt-4o, deepseek/deepseek-chat, etc.

# Kubernetes Configuration
KUBECONFIG_PATH=~/.kube/config
```

> The frontend reads its backend URL from `NEXT_PUBLIC_API_BASE_URL` (defaults to `http://localhost:8000`). Create a `frontend/.env.local` if you need to override it — e.g. when running via Docker Compose, point it at `http://localhost:8001`.

### 3. Point Docker Compose at your kubeconfig

`docker-compose.yml` mounts a host kubeconfig directory into the backend container so `kubectl` can reach your cluster:

```yaml
volumes:
  - ./backend:/app
  - /home/saransh/.kube:/root/.kube:ro   # ⚠️ change this to YOUR kubeconfig directory
```

Update that path (e.g. `~/.kube` or `${HOME}/.kube`) before starting the stack, otherwise the backend won't see your cluster contexts.

If you're testing against a [Kind](https://kind.sigs.k8s.io/) cluster, also attach it to the `kind` external Docker network so the backend container can reach the control plane:

```bash
docker network connect kind <your-kind-network-name>   # usually already named "kind"
```

### 4. Launch the stack

```bash
docker compose up --build
```

### 5. Open the console

| Service | URL |
|---|---|
| 🖥️ Frontend Console | [http://localhost:3000](http://localhost:3000) |
| 🔌 Backend API | [http://localhost:8001](http://localhost:8001) |
| 📄 Interactive API Docs (Swagger) | [http://localhost:8001/docs](http://localhost:8001/docs) |

Sign up / sign in, pick a cluster context from the dropdown, and click **Investigate Cluster**.

---

## 🔧 Configuration Reference

### `backend/.env`

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | *(required)* | API key used to authenticate with OpenRouter's `/chat/completions` endpoint. |
| `OPENROUTER_MODEL` | `google/gemini-2.0-flash-001` | Any OpenRouter-supported model slug — swap in Claude, GPT-4, DeepSeek, etc. |
| `KUBECONFIG_PATH` | `~/.kube/config` | Path to the kubeconfig the backend uses for every `kubectl` invocation. |

### `frontend` environment

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Base URL the frontend uses to reach the FastAPI backend. |

---

## 🧪 Try It Yourself — Test Scenarios

The `k8s-test-scenarios/` folder ships four ready-made broken manifests so you can see the agent in action immediately:

```bash
# 1. CrashLoopBackOff from a missing required environment variable
kubectl apply -f k8s-test-scenarios/01-crashloop-missing-env.yaml

# 2. ImagePullBackOff from an invalid image tag
kubectl apply -f k8s-test-scenarios/02-imagepull-invalid-tag.yaml

# 3. OOMKilled from an undersized memory limit
kubectl apply -f k8s-test-scenarios/03-oom-memory-limit.yaml

# 4. Service selector mismatch — no matching endpoints
kubectl apply -f k8s-test-scenarios/04-service-selector-mismatch.yaml
```

Then open the console and click **Investigate Cluster** — the agent will surface each failure, explain the root cause, and recommend a fix.

Clean up afterwards:

```bash
kubectl delete -f k8s-test-scenarios/
```

---

## 📡 API Reference

The backend exposes a small, focused REST surface (full interactive docs at `/docs`):

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness/health check. Returns `{"status": "healthy", "service": "ai-kubernetes-agent"}`. |
| `GET` | `/clusters` | Lists all contexts from the configured `kubeconfig`, plus the current context. |
| `POST` | `/investigate` | Runs the full 5-stage investigation + AI diagnosis pipeline. |

**`POST /investigate` request body:**

```json
{
  "namespace": "default",
  "context": "kind-tws-cluster",
  "investigation_id": "optional-id-for-realtime-progress-tracking"
}
```

All fields are optional — omitting `namespace`/`context` scans the current context across all namespaces.

**Response shape** (`FullDiagnosisResponse`):

```json
{
  "status": "success",
  "investigation": {
    "pods": { "healthy": false, "total_pods": 3, "problematic_pods": [ /* ... */ ] },
    "logs": [ /* per-pod log entries */ ],
    "events": { "total_events": 12, "warning_events": [ /* ... */ ], "has_issues": true },
    "deployments": { "healthy": true, "total_deployments": 2, "unhealthy_deployments": [] },
    "network": { "total_services": 4, "problematic_services": [], "has_issues": false }
  },
  "diagnosis": {
    "root_cause": "...",
    "explanation": "...",
    "fix": "...",
    "kubectl_commands": ["kubectl ..."],
    "prevention": "...",
    "confidence": 95,
    "confidence_reasoning": "..."
  }
}
```

---

## 🔐 Security & Hardening Notes

This project is a demo/reference implementation. Before running it against a production cluster, consider:

- **Least-privilege kubeconfig** — scope the mounted kubeconfig to a read-only service account limited to the namespaces you want the agent to inspect, rather than a full-admin context.
- **CORS** — `main.py` currently allows all origins (`allow_origins=["*"]`); lock this down to your frontend's origin before deploying publicly.
- **Realtime credentials** — `services/realtime.py` currently ships a hardcoded InsForge anonymous token/URL for the demo project; move these to environment variables and rotate them for your own InsForge project before going to production.
- **Secrets management** — never commit populated `.env` files; use your platform's secret manager (Docker secrets, Kubernetes Secrets, Vault, etc.) in real deployments.
- **LLM data exposure** — investigation payloads (pod logs, event messages) are sent to your chosen OpenRouter model provider. Review your organization's data-handling policies before pointing this at clusters with sensitive log content.

---

## 🗺️ Roadmap

Ideas for extending the project:

- [ ] Node-level diagnostics (disk pressure, `NotReady` nodes, taints/tolerations)
- [ ] One-click "Apply Fix" — execute the recommended `kubectl` commands directly from the UI (with confirmation)
- [ ] Slack / PagerDuty / webhook notifications on new incidents
- [ ] Streaming LLM responses instead of a single blocking completion
- [ ] Multi-tenant RBAC-aware cluster access
- [ ] Prometheus/Grafana metrics correlation alongside events and logs
- [ ] Automated regression tests using the bundled `k8s-test-scenarios/`

---

## 🤝 Contributing

Contributions are welcome! To propose a change:

1. Fork the repo and create a feature branch.
2. Make your changes (keep backend modules single-responsibility, matching the existing `kubernetes/` inspector pattern).
3. Test locally against a Kind/Minikube cluster using the bundled `k8s-test-scenarios/`.
4. Open a pull request describing the change and any new environment variables.

---

## 📄 License

No license file is currently included in this repository. Add a `LICENSE` file (MIT, Apache-2.0, etc.) to clarify usage terms before distributing or accepting external contributions.

---

<div align="center">

Built with ☸️ Kubernetes, ⚡ FastAPI, ⚛️ Next.js, and 🤖 your favorite LLM.

</div>
