# How to Run the Adaptive UEBA Codebase

> **Comprehensive Execution & Operations Guide**  
> *Adaptive UEBA Insider Threat Detection System (CMU CERT r5.2)*  
> *Contamination-Resistant Baseline Governance & Multi-Model Ensemble*

---

## ⚡ Quick Terminal Commands Cheat Sheet (5 Terminals)

Copy and paste these exact commands into 5 separate terminal tabs to run the complete stack:

| Terminal | Purpose | Working Directory (`CWD`) | Exact Command to Run |
| :---: | :--- | :--- | :--- |
| **Terminal 1** | **WSL (Redis 7.0 Broker)** | `D:\Chetan Sir\cyberProject` | `wsl`<br/>*(then inside WSL: `sudo service redis-server start`)* |
| **Terminal 2** | **Django REST API (Backend)** | `D:\Chetan Sir\cyberProject\backend` | `venv\Scripts\activate`<br/>`python manage.py runserver 127.0.0.1:8000` |
| **Terminal 3** | **Celery LLM Worker (`llm` Queue)** | `D:\Chetan Sir\cyberProject\backend` | `venv\Scripts\activate`<br/>`python -m celery -A config worker -Q llm -c 2 -n llm@%h -l info -P solo` |
| **Terminal 4** | **Celery Governance Worker (`governance` Queue)** | `D:\Chetan Sir\cyberProject\backend` | `venv\Scripts\activate`<br/>`python -m celery -A config worker -Q governance -c 1 -n gov@%h -l info -P solo` |
| **Terminal 5** | **Vite React UI (Frontend)** | `D:\Chetan Sir\cyberProject\frontend` | `npm run dev` |

---

## 1. System Architecture Overview

The system consists of 5 collaborating components:

```mermaid
graph TD
    Client["Browser UI (Vite + React)<br/>http://localhost:3000"]
    API["Django REST API<br/>http://127.0.0.1:8000/api/v1/"]
    DB[("SQLite Database<br/>db.sqlite3")]
    Redis[("Redis 7.0 (WSL/Docker)<br/>Port 6379")]
    CeleryLLM["Celery Worker (Queue: llm)<br/>Claude 3.5 Sonnet Synthesis"]
    CeleryGov["Celery Worker (Queue: governance)<br/>4-Stage Drift Governance Engine"]

    Client -->|HTTP / JSON| API
    API -->|ORM Queries| DB
    API -->|Enqueue Task (HTTP 202)| Redis
    Redis -->|Dispatch Task| CeleryLLM
    Redis -->|Dispatch Task| CeleryGov
    CeleryLLM -->|Save Explanation| DB
    CeleryGov -->|Save Governance Log| DB
    Client -->|Poll Status (2.5s)| API
```

---

## 2. Prerequisites

| Component | Minimum Version | Notes |
| :--- | :--- | :--- |
| **Python** | 3.10 or 3.11 | Standard Python 64-bit |
| **Node.js** | v18.0+ or v20.0+ | Includes npm package manager |
| **Redis** | 7.0+ | Run via WSL (Ubuntu) or Docker |
| **OS** | Windows 10/11 | Uses PowerShell or Command Prompt |

---

## 3. Detailed Step-by-Step Terminal Instructions

---

### Terminal 1: Redis Broker (WSL Ubuntu)

Redis serves as the message broker for Celery asynchronous queues.

* **Working Directory:** `D:\Chetan Sir\cyberProject`

```bash
# 1. Launch WSL Ubuntu environment
wsl

# 2. Inside the WSL shell, start the Redis service
sudo service redis-server start

# 3. Verify Redis is running and listening on port 6379
redis-cli ping
# Expected response: PONG
```

*(Alternatively, if running via Docker Desktop: `docker run -d --name ueba-redis -p 6379:6379 redis:7-alpine`)*

---

### Terminal 2: Django REST Backend Server

Handles all API endpoints: User Leaderboard, Risk Trajectories, Alerts Feed, Verdict Submissions, Baseline Governance Logs, and Metrics.

* **Working Directory:** `D:\Chetan Sir\cyberProject\backend`

```powershell
# 1. Navigate to backend directory
cd "D:\Chetan Sir\cyberProject\backend"

# 2. Activate Python Virtual Environment
.\venv\Scripts\activate

# 3. (Optional) Run migrations to verify database schema
python manage.py migrate

# 4. Launch Django Development Server on port 8000
python manage.py runserver 127.0.0.1:8000
```
* **Backend API Base:** `http://127.0.0.1:8000/api/v1/`
* **Django Admin Console:** `http://127.0.0.1:8000/admin/`

---

### Terminal 3: Celery Worker 1 — LLM Explanation Queue (`llm`)

Processes background Claude 3.5 Sonnet incident explanations, TreeSHAP feature attributions, and FaithLens zero-hallucination validation.

* **Working Directory:** `D:\Chetan Sir\cyberProject\backend`

```powershell
# 1. Navigate to backend directory
cd "D:\Chetan Sir\cyberProject\backend"

# 2. Activate Python Virtual Environment
.\venv\Scripts\activate

# 3. Launch Celery Worker for LLM queue
python -m celery -A config worker -Q llm -c 2 -n llm@%h -l info -P solo
```

> **Why `-P solo`?** On Windows, Python's default multiprocessing (`fork`) is unsupported. The `-P solo` parameter forces Celery to use a thread-safe Windows execution pool and prevents `billiard` multiprocessing errors.

---

### Terminal 4: Celery Worker 2 — Baseline Governance Queue (`governance`)

Executes the 4-stage drift governance engine: drift rate checks, peer cluster deviation scoring, monotonic trend validation, and baseline quarantine locks.

* **Working Directory:** `D:\Chetan Sir\cyberProject\backend`

```powershell
# 1. Navigate to backend directory
cd "D:\Chetan Sir\cyberProject\backend"

# 2. Activate Python Virtual Environment
.\venv\Scripts\activate

# 3. Launch Celery Worker for Governance queue
python -m celery -A config worker -Q governance -c 1 -n gov@%h -l info -P solo
```

---

### Terminal 5: Vite React Frontend Server

Compiles and serves the interactive SOC Command Center UI with Hot Module Replacement (HMR).

* **Working Directory:** `D:\Chetan Sir\cyberProject\frontend`

```powershell
# 1. Navigate to frontend directory
cd "D:\Chetan Sir\cyberProject\frontend"

# 2. (First time only) Install npm dependencies
npm install

# 3. Start Vite React Development Server
npm run dev
```
* **Frontend Web App:** `http://localhost:3000/`

---

## 4. One-Click Batch Script Launcher

You can also use the included Windows batch script to launch both servers simultaneously:

```bat
# From repository root:
START_APPLICATION.bat
```

This automatically:
1. Starts the Django Backend Server (`http://127.0.0.1:8000/api/v1/`)
2. Starts the Vite Frontend Server (`http://localhost:3000/`)
3. Opens your default web browser to `http://localhost:3000/`

*(Note: Ensure Redis in WSL or Docker is started before triggering Celery tasks).*

---

## 5. System Navigation & Route Map

| View Name | Route | Purpose & Key Features |
| :--- | :--- | :--- |
| **Risk Dashboard** | [`/`](http://localhost:3000/) | SOC Command Center: KPI Stat Cards, User Risk Leaderboard, Live Threat Stream, Quick Triage buttons. |
| **User Profile Deep-Dive** | `/users/:id` | 30-Day risk trajectory line chart, Composite risk gauge, Peer cluster deviation, Top-5 TreeSHAP drivers. |
| **Incident Timeline** | [`/timeline`](http://localhost:3000/timeline) | Multi-channel audit trail across Logons, USB Removable Media, Email attachments, and HTTP Web activity. |
| **Analyst Feedback** | [`/feedback`](http://localhost:3000/feedback) | Human-in-the-Loop adjudication: Submit True Positive / False Positive verdicts and manual baseline quarantine overrides. |
| **AI Threat Chat** | [`/chat`](http://localhost:3000/chat) | Context-grounded Claude 3.5 Sonnet SOC Copilot with zero-hallucination constraint guarantees. |
| **Alert-Scoped Chat** | `/alerts/:id/chat` | Direct copilot triage loaded with exact behavioral telemetry and Celery async explanation generator. |
| **Admin Metrics** | [`/admin/metrics`](http://localhost:3000/admin/metrics) | M.Tech Thesis validation benchmarks (E1–E5), Confusion Matrix, and Poisoning Simulation comparisons. |

---

## 6. Environment Variables (`backend/.env`)

If customizing configurations, edit `backend/.env`:

```ini
DJANGO_SECRET_KEY=django-insecure-ueba-adaptive-threat-detection-key-2026-2027
DJANGO_SETTINGS_MODULE=config.settings.dev
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# SQLite Database (Default)
DATABASE_URL=sqlite:///db.sqlite3

# Redis Broker URL (Local via WSL or Docker)
REDIS_URL=redis://localhost:6379/0

# Anthropic Claude API Key (Optional: system uses grounded offline cache if key not present)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

---

## 7. Common Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **Vite port 3000 in use** | A previous dev server is running | Vite will automatically switch to port 3001, or kill the process using port 3000. |
| **Celery `ValueError: not enough values to unpack`** | Standard Celery fork pool on Windows | Add `-P solo` flag when starting Celery worker command. |
| **Redis connection refused (Error 10061)** | Redis server is not running | Run `wsl` and execute `sudo service redis-server start`. |
| **API returns 404 for `/api/v1/verdicts/`** | Incorrect URL path | Ensure you hit `/api/v1/verdicts/alerts/{id}/verdict/` (or use the built-in alias). |
| **Changes not reflecting in UI** | Vite HMR caching | Hard-refresh your browser with `Ctrl + F5` or click the Refresh icon in the top Navbar. |
