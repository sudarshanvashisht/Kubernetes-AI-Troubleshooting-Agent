# Kubernetes AI Troubleshooting Agent ☸🤖

An autonomous AI Site Reliability Engineer (SRE) designed to interrogate your Kubernetes cluster, correlate telemetry and configuration evidence, and deliver instant root-cause diagnoses along with copy-paste-ready `kubectl` remediation fixes.

---

## 🚀 Key Features

*   **☸️ Multi-Cluster Selector**: Dynamically reads and lists all available contexts from your local `kubeconfig` — switch clusters from a dropdown, no restarts needed.
*   **🧭 Namespace Scoping**: Optionally scope investigations to specific namespaces instead of scanning the whole cluster.
*   **⏱️ Real-Time Pipeline Progress**: Streams a live diagnostic checklist (`✓ Checking Pods`, `✓ Reading Logs` ...) to the browser over InsForge Socket.IO.
*   **🕵️ Five-Stage Evidence Collection**: Self-healing inspectors for pods, logs, events, deployments, and services/DNS.
*   **🤖 LLM-Powered Root Cause Analysis**: Correlates configuration specs, warning events, restart counts, and container exit codes (like OOMKilled exit code 137).
*   **📋 Actionable Remediation**: Generates ready-to-run `kubectl` patch commands, prevention guidance, and confidence scores.
*   **🔒 Authenticated Console**: Gatekeeper secure access with email verification (powered by InsForge Auth).

---

## 📸 Console Screenshots

### 1. Simulated Kubernetes Failure State
![Simulated Kubernetes Failure](./docs/assets/01-k8s-failure.png)

### 2. Sleek Dashboard Console & Selector
![SRE Dashboard Cluster Selector](./docs/assets/02-dashboard-cluster.png)

### 3. Diagnosis Report & Detailed Analysis
![Root Cause & Detailed Analysis](./docs/assets/03-diagnosis-report.png)

### 4. Actionable, Copyable Remediation Commands
![Copyable Kubectl Remediation Commands](./docs/assets/04-kubectl-commands.png)

### 5. Incident History & Prevention Guidance
![Incident History & Prevention Guidelines](./docs/assets/05-prevention-history.png)

---

## 🏗️ High-Level Architecture

```text
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
FastAPI Backend (Orchestration Layer)
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
LLM Reasoning (OpenRouter via InsForge Key)
                │
                ▼
Root Cause Analysis
                │
                ▼
Suggested Fix Generated
                │
                ├── Save Investigation History (InsForge)
                │
                ├── Realtime Progress Updates (InsForge)
                │
                ▼
Frontend Receives Result
                │
                ▼
User sees Diagnosis
```

---

## 🔄 Example Failure Flow

```text
Issue:
Payment service unavailable

Agent Investigation:
✓ Pod Status Checked
✓ Logs Collected
✓ Events Analyzed

Detected Problem:
CrashLoopBackOff

Root Cause:
DATABASE_URL environment variable missing

Confidence:
94%

Suggested Fix:
Update deployment.yaml and add secret reference

Prevention:
Add startup validation checks
```

---

## 🛠️ Supported Kubernetes Failures

*   `CrashLoopBackOff`
*   `ImagePullBackOff` / `ErrImagePull`
*   `OOMKilled` (Exit Code 137)
*   `Pending Pods` / Scheduling issues
*   Resource Exhaustion (CPU/Memory limits)
*   Deployment Rollout Failures
*   Service Selector Mismatches
*   DNS Resolution Problems
*   Readiness/Liveness Probe Failures
*   Networking & Ingress config issues

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
