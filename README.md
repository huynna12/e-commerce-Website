# H-Commerce

Full-stack e-commerce app with a Django REST Framework backend and a React (Vite) frontend.

## Features

- JWT auth (login/register), profile pages
- Items: list/detail, create/edit (seller flow)
- Cart + checkout flow with stock validation
- Orders: buyer order history + order detail
- Buyer shipping edits (while order is processing)
- Partial cancellation workflow: buyer requests cancellation for specific order items; seller approves/denies per item
- Seller dashboard: sellers see orders that include their items + pending cancellation requests

## Tech stack

- Backend: Django, Django REST Framework, SimpleJWT, drf-spectacular
- Frontend: React, Vite, TailwindCSS
- DB: SQLite (local), supports Postgres via `DATABASE_URL`

## Local setup (Windows)

### 1) Backend

```powershell
cd backend
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend runs at `http://127.0.0.1:8000/`.

API docs (Swagger): `http://127.0.0.1:8000/api/docs/`

### 2) Frontend

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Frontend runs at `http://localhost:5173/` (or the next free port).

## Seed demo items

```powershell
cd backend
python manage.py seed_items 50
```

## Run tests

```powershell
cd backend
python manage.py test
```

## Deployment notes (quick)

- Frontend (Vercel/Netlify): set `VITE_API_URL` to your deployed backend URL (ending with `/api/`).
- Backend (Render/Railway/Fly): set env vars from [backend/.env.example](backend/.env.example), use Postgres (`DATABASE_URL`), and run `python manage.py migrate` and `python manage.py collectstatic`.
- Media uploads: for production, move `MEDIA_ROOT` to S3/Cloud storage (or treat uploads as non-persistent).

