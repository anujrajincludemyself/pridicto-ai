# Pridicto — Smart Indian Railway Route Finder

A full-stack web app using **Django + React** with a BFS graph algorithm and Claude AI.

## Quick Start

### 1. Backend (Django)
```batch
# Run this in a terminal
start_backend.bat
```
Or manually:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # Fill in your API keys
python manage.py migrate
python manage.py runserver
```

### 2. Frontend (React)
```batch
# Run this in a second terminal
start_frontend.bat
```
Or manually:
```bash
cd frontend
npm install
npm run dev
```

App → **http://localhost:3000**  
API → **http://localhost:8000/api/**

---

## API Keys Required (all free)

| Key | Where to get |
|-----|--------------|
| `DJANGO_SECRET_KEY` | Any random 50-char string |
| `SUPABASE_URL` + keys | https://supabase.com → New project → Settings → API |
| `UPSTASH_REDIS_REST_URL` + token | https://upstash.com → Create Redis DB → REST API |
| `RAPIDAPI_KEY` | https://rapidapi.com → Search "Indian Railway IRCTC" → Subscribe free |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com → API Keys |

**Best AI Model:** `claude-3-haiku-20240307` — fast, cheap, accurate for intent parsing.

> **Without API keys the app still works** using built-in mock train data!

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/` | Health check |
| GET | `/api/routes/search/?from=NDLS&to=BCT&date=20241215` | Search routes |
| POST | `/api/routes/ai-search/` `{"query": "..."}` | AI natural language search |
| GET | `/api/stations/search/?q=Delhi` | Autocomplete stations |
| GET | `/api/train/status/?train_no=12001&date=20241215` | Live status |
| GET | `/api/routes/popular/` | Popular routes list |
