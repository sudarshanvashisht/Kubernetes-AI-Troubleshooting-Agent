# Kubernetes AI Troubleshooting Agent ☸🤖

An AI-powered Site Reliability Engineering (SRE) companion designed to dynamically troubleshoot Kubernetes cluster failures. The agent connects to your clusters, collects telemetry logs, events, and resources, and analyzes them using state-of-the-art Large Language Models (LLMs) to deliver instant root cause analyses, fix suggestions, and prevention guidelines.

---

## 🚀 Key Features

*   **☸ Multi-Cluster Selector**: Dynamically reads and lists all available contexts from your `kubeconfig` on the local machine.
*   **⏱️ Real-time Pipeline Progress**: Emits step-by-step progress checklist logs over InsForge Socket.IO WebSocket.
*   **🤖 Intelligent AI Reasoning**: Correlates cluster events, pod status, container logs, deployment specs, and service mappings.
*   **📋 Actionable Remediations**: Generates ready-to-run copyable `kubectl` commands and YAML patches.
*   **🔒 Secure Operations**: Keeps cluster keys safe and offers secure anonymous authentication.

---

## 📸 Console Screenshots

### 1. Simulated Kubernetes Failure State
![Simulated Kubernetes Failure](./docs/assets/01-k8s-failure.png)

### 2. Sleek Dashboard Console
![SRE Dashboard Cluster Selector](./docs/assets/02-dashboard-cluster.png)

### 3. Diagnosis Report & Detailed Analysis
![Root Cause & Detailed Analysis](./docs/assets/03-diagnosis-report.png)

### 4. Actionable Remediation Commands
![Copyable Kubectl Remediation Commands](./docs/assets/04-kubectl-commands.png)

### 5. Incident History & Prevention Guidelines
![Incident History & Prevention Guidelines](./docs/assets/05-prevention-history.png)

---

## 🏗️ High-Level Architecture

```text
High Level Architecture

┌────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                     │
│                                                            │
│  Pods | Deployments | Services | Events | Logs            │
│                                                            │
│  This is where failures happen and evidence exists         │
└────────────────────────────────────────────────────────────┘
                              │
                              │ kubectl / Kubernetes API
                              ▼
┌────────────────────────────────────────────────────────────┐
│                  Investigation Layer                      │
│                                                            │
│ Responsibility:                                            │
│ - Connect to Kubernetes cluster                            │
│ - Collect troubleshooting signals                          │
│ - Gather debugging evidence                                │
│                                                            │
│ Components:                                                │
│                                                            │
│  1. Pod Inspector                                          │
│     - Get pod health                                       │
│     - Detect CrashLoopBackOff                              │
│     - Detect Pending/Error states                          │
│                                                            │
│  2. Logs Collector                                         │
│     - Read pod logs                                        │
│     - Capture container errors                             │
│                                                            │
│  3. Events Analyzer                                        │
│     - Read Kubernetes events                               │
│     - Detect scheduling/image failures                     │
│                                                            │
│  4. Deployment Inspector                                   │
│     - Inspect deployment status                            │
│     - Verify rollout health                                │
│                                                            │
│  5. Network Inspector                                      │
│     - Check services                                       │
│     - Validate selectors                                   │
│     - Investigate DNS/networking issues                    │
└────────────────────────────────────────────────────────────┘
                              │
                              │ Structured Investigation Data
                              ▼
┌────────────────────────────────────────────────────────────┐
│                  AI Kubernetes Agent                      │
│                                                            │
│ Responsibility:                                            │
│ - Understand Kubernetes failures                           │
│ - Correlate logs + events + deployment state               │
│ - Identify root cause                                      │
│ - Recommend fixes                                          │
│                                                            │
│ Components:                                                │
│                                                            │
│  1. Prompt Builder                                         │
│     - Convert investigation data into LLM prompt           │
│                                                            │
│  2. LLM Reasoning Layer                                    │
│     - Uses OpenRouter API Key from InsForge                │
│     - Supports models like:                                │
│       - Claude                                              │
│       - GPT                                                 │
│       - DeepSeek                                            │
│                                                            │
│  3. Root Cause Analyzer                                    │
│     - Detect primary issue                                 │
│     - Correlate signals                                    │
│                                                            │
│  4. Fix Recommendation Engine                              │
│     - Suggest kubectl fixes                                │
│     - Recommend YAML updates                               │
│                                                            │
│  5. Confidence Scoring                                     │
│     - Confidence % for diagnosis                           │
└────────────────────────────────────────────────────────────┘
                              │
                              │ Investigation Result
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    InsForge Backend                       │
│                                                            │
│ Responsibility:                                            │
│ - Authentication                                           │
│ - Backend APIs                                             │
│ - Investigation history                                    │
│ - Realtime investigation updates                           │
│                                                            │
│ Components:                                                │
│                                                            │
│  1. Authentication                                         │
│     - User login                                           │
│                                                            │
│  2. API Layer                                              │
│     - Trigger investigations                               │
│     - Return AI analysis                                   │
│                                                            │
│  3. Investigation History                                  │
│     - Store previous incidents                             │
│     - Save root cause reports                              │
│                                                            │
│  4. Realtime Updates                                       │
│     - Live investigation progress                          │
│                                                            │
│ Example:                                                    │
│  ✓ Checking pods                                           │
│  ✓ Reading logs                                            │
│  ✓ Analyzing events                                        │
│  ✓ Finding root cause                                      │
└────────────────────────────────────────────────────────────┘
                              │
                              │ API Response
                              ▼
┌────────────────────────────────────────────────────────────┐
│                     Frontend Dashboard                    │
│                                                            │
│ Responsibility:                                            │
│ - Trigger investigation                                    │
│ - Show realtime progress                                   │
│ - Display root cause                                       │
│ - Show suggested fixes                                     │
│ - Show investigation history                               │
│                                                            │
│ Example UI:                                                 │
│                                                            │
│ Incident: Payment Service Failure                          │
│                                                            │
│ Status: Investigating...                                   │
│                                                            │
│ ✓ Pods Checked                                             │
│ ✓ Events Analyzed                                          │
│ ✓ Logs Processed                                           │
│                                                            │
│ Root Cause: ImagePullBackOff                               │
│                                                            │
│ Suggested Fix:                                             │
│ Update invalid image tag                                   │
└────────────────────────────────────────────────────────────┘
                              │
                              │ Deploy Entire App
                              ▼
┌────────────────────────────────────────────────────────────┐
│                     InsForge Deployment                   │
│                                                            │
│ Responsibility:                                            │
│ - Deploy frontend                                          │
│ - Deploy backend                                           │
│ - Generate public URL                                      │
│                                                            │
│ Output:                                                     │
│                                                            │
│ https://ai-k8s-agent.public-url.app                        │
│                                                            │
│ Enables public access to the troubleshooting platform      │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 End-to-End Workflow

```text
User clicks "Investigate Cluster"
                │
                ▼
Frontend sends API request
                │
                ▼
FastAPI Backend
      (Orchestration Layer)
                │
                ├── Authenticate User (InsForge)
                │
                ▼
Investigation Layer
                │
                ├── Check Pods
                ├── Read Logs
                ├── Analyze Events
                ├── Inspect Deployments
                └── Check Networking
                │
                ▼
AI Kubernetes Agent
                │
                ▼
LLM Reasoning
      (OpenRouter via InsForge Key)
                │
                ▼
Root Cause Analysis
                │
                ▼
Suggested Fix Generated
                │
                ├── Save Investigation History
                │        (InsForge)
                │
                ├── Realtime Progress Updates
                │        (InsForge)
                │
                ▼
Frontend Receives Result
                │
                ▼
User sees Diagnosis
```

---

## 🛠️ Supported Kubernetes Failures

Our agent is capable of identifying, explaining, and remediating the following cluster failures:
*   `CrashLoopBackOff`
*   `ImagePullBackOff` / `ErrImagePull`
*   `OOMKilled` (Exit Code 137)
*   `Pending Pods` / Scheduling bottlenecks
*   Resource Exhaustion (CPU/Memory limits)
*   Deployment Rollout Failures
*   Service Selector Mismatches
*   DNS Resolution Problems
*   Readiness/Liveness Probe Failures
*   Networking & Ingress config issues

---

## ⚡ Quick Start (Running Locally)

### Prerequisites
*   Docker & Docker Compose
*   A running Kubernetes cluster (e.g. Minikube or Kind) with kubeconfig configured at `~/.kube/config`.

### Setup environment

1. Clone or download the codebase.
2. Initialize environment configs:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```
3. Start the services:
   ```bash
   docker compose up --build
   ```
4. Access the applications:
   - **Frontend Console**: [http://localhost:3000](http://localhost:3000)
   - **Backend API**: [http://localhost:8001](http://localhost:8001)
