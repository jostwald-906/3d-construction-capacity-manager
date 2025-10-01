from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.routers import auth, projects, models, grid, trades, capacities, allocations, users

app = FastAPI(title="3D Construction Capacity Manager", version="1.0.0")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(grid.router, prefix="/grid", tags=["grid"])
app.include_router(trades.router, prefix="/trades", tags=["trades"])
app.include_router(capacities.router, prefix="/capacities", tags=["capacities"])
app.include_router(allocations.router, prefix="/allocations", tags=["allocations"])

@app.get("/health")
def health():
    return {"status": "ok"}
