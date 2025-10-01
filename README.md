# 3D Construction Capacity Manager

Production-ready web app for grid-based workforce planning on 3D construction models.  
Stack: FastAPI + PostgreSQL/PostGIS + SQLAlchemy + JWT | React + Vite + Three.js + D3 + Tailwind.

## Features
- User-defined 3D grid generation (X,Y,Z) over construction models
- Role-based auth: `admin`, `trade_manager`, `viewer`
- CRUD for trades, grid cells, capacities, and allocations
- Capacity validation (total and trade-specific) per cell per date
- 3D grid view with over-capacity highlighting
- Mobile responsive UI
- Dockerized dev environment
- Production deployment: Vercel (frontend) + Fly.io (backend) + Supabase (PostgreSQL/PostGIS)

## Quick Start (Docker - Local Dev)
```bash
cp .env.sample .env
docker compose up --build
open http://localhost:5173
open http://localhost:8000/docs
```

Default login: `admin` / `admin` (change in production!)

## Manual Setup (Local)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
createdb capacity_manager
psql -d capacity_manager -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql -d capacity_manager -f db/init.sql
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm ci
npm run dev
```

## Production Deployment

### 1. Database (Supabase)
```bash
# Enable PostGIS extension in Supabase dashboard
# Run schema initialization:
psql "postgresql://user:pass@host:5432/db?sslmode=require" -f backend/db/init.sql
```

### 2. Backend (Fly.io)
```bash
cd backend
fly launch --name your-app-api
fly secrets set JWT_SECRET="your-secret-here"
fly secrets set DATABASE_URL="postgresql://..."
fly secrets set CORS_ORIGINS="https://your-app.vercel.app"
fly deploy
```

### 3. Frontend (Vercel)
```bash
cd frontend
vercel --prod
# Set environment variable: VITE_BACKEND_URL=https://your-app-api.fly.dev
```

## Testing
```bash
cd backend && pytest
cd frontend && npm test
```

## Architecture Notes
- IFC/Revit parsing stubbed; uses mock submarine model bounds (170x12x13)
- Capacity validation treats null num_workers as 1
- Date-based scheduling at day-level granularity
- For large grids (>2k cells), switch to Three.js InstancedMesh
