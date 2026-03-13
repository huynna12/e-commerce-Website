# H-Commerce Frontend

React + Vite frontend for the H-Commerce project.

## Requirements

- Node.js 18+ recommended

## Local setup

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

## Environment variables

- `VITE_API_URL` (required): backend base API URL (example: `http://127.0.0.1:8000/api/`)

Optional (only for sourcemap uploads during `npm run build`):

- `SENTRY_AUTH_TOKEN`

## Scripts

- `npm run dev` - start dev server
- `npm run build` - production build
- `npm run preview` - preview build locally
- `npm run lint` - run ESLint
