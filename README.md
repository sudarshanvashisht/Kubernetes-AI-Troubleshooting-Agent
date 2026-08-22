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
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

</div>

---

## 🚀 Key Features

*   **☸️ Multi-Cluster Selector**: Dynamically lists and switches every context from your local `kubeconfig` dropdown.
*   **⏱️ Real-Time Pipeline Progress**: Streams live progress checklists (`✓ Checking Pods`, `✓ Reading Logs` ...) over InsForge Socket.IO.
*   **🕵️ Five-Stage Evidence Collection**: Automated inspectors for pods, logs, events, deployments, and services/DNS.
*   **🤖 LLM Root Cause Analysis**: Correlates cluster warnings, restart loops, OOM error signals, and selector mismatches.
*   **📋 Actionable Remediation**: Generates ready-to-run `kubectl` command patches, prevention guidance, and confidence scores.
*   **🔒 Authenticated Console**: Gatekeeper secure access with email OTP validation (powered by InsForge Auth).

---

## 📸 Console Screenshots

### 1. Simulated Kubernetes Failure
![Simulated Kubernetes Failure](./docs/assets/01-k8s-failure.png)

### 2. Sleek Dashboard Console
![SRE Dashboard Cluster Selector](./docs/assets/02-dashboard-cluster.png)

### 3. Diagnosis Report & Detailed Analysis
![Root Cause & Detailed Analysis](./docs/assets/03-diagnosis-report.png)

### 4. Actionable Remediation Commands
![Copyable Kubectl Remediation Commands](./docs/assets/04-kubectl-commands.png)

### 5. Incident History & Prevention Guidance
![Incident History & Prevention Guidelines](./docs/assets/05-prevention-history.png)

---

## 🏗️ High-Level Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                      │
│         Pods | Deployments | Services | Events | Logs      │
└────────────────────────────────────────────────────────────┘
                              │  kubectl / Kubernetes API
                              ▼
┌────────────────────────────────────────────────────────────┐
│                   Investigation Layer                      │
│  - Pod Inspector        - Logs Collector                   │
│  - Events Analyzer      - Deployment & Network Inspectors  │
└────────────────────────────────────────────────────────────┘
                              │  Structured Investigation Data
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    AI Kubernetes Agent                      │
│  - Prompt Builder       - OpenRouter LLM Reasoning Layer   │
│  - Root Cause Analyzer  - Fix Recommendation Engine        │
└────────────────────────────────────────────────────────────┘
                              │  Result & History
                              ▼
┌────────────────────────────────────────────────────────────┐
│              InsForge Backend & Dashboard                  │
│  - Auth Control         - Realtime Socket.IO Checklists    │
│  - Incident History     - Next.js 16 Responsive UI         │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 End-to-End Workflow

```text
User clicks "Investigate Cluster" ──► Next.js Dashboard sends API request 
  ──► FastAPI orchestrates pipeline (emits realtime progress per check)
  ──► Gathers Pods, Logs, Events, Deployments, and Networking evidence
  ──► AI agent builds prompt ──► OpenRouter feeds LLM (Claude/GPT/Gemini/DeepSeek)
  ──► Root Cause & fix returned ──► Dashboard renders copy-ready remediations
```

---

## 🧪 Try It Yourself — Test Scenarios

Verify the agent locally against these ready-made manifests under `k8s-test-scenarios/`:

```bash
# Apply test scenarios (CrashLoopBackOff, ImagePullBackOff, OOMKilled, Service selector mismatch)
kubectl apply -f k8s-test-scenarios/

# Open dashboard and run diagnosis. Clean up when finished:
kubectl delete -f k8s-test-scenarios/
```

---

## ⚡ Quick Start

### 1. Configure environment variables
```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env` with your `OPENROUTER_API_KEY`, chosen model, and `KUBECONFIG_PATH`.

### 2. Point Docker Compose at your kubeconfig directory
Update the volume mount path in `docker-compose.yml` to point to your host config folder (e.g. `/home/saransh/.kube` or `~/.kube`).

### 3. Launch the stack
```bash
docker compose up --build
```
Access the **Console UI** at [http://localhost:3000](http://localhost:3000).

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).
