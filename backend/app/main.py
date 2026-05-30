from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers.admin import router as admin_router
from app.routers.portal import router as portal_router
from app.routers.solicitudes import router as solicitudes_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="CrediActiva API",
    description="API de solicitudes de crédito — Cooperativa Huancayo, Perú",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(solicitudes_router)
app.include_router(admin_router)
app.include_router(portal_router)


@app.get("/health", tags=["Sistema"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "servicio": "CrediActiva API"}
