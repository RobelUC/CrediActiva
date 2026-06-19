import os

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CREDIT_SERVICE_URL = os.getenv("CREDIT_SERVICE_URL", "http://localhost:8002")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8003")
PORTAL_SERVICE_URL = os.getenv("PORTAL_SERVICE_URL", "http://localhost:8004")

app = FastAPI(
    title="CrediActiva API Gateway",
    description="Punto de entrada único — enruta a microservicios",
    version="2.0.0",
)

_cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:4200")
CORS_ORIGINS = [origin.strip() for origin in _cors_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolver_servicio(path: str, method: str) -> str | None:
    if path.startswith("/api/v1/auth"):
        return AUTH_SERVICE_URL
    if path.startswith("/api/v1/solicitudes"):
        return CREDIT_SERVICE_URL
    if path.startswith("/api/v1/admin/socios"):
        return AUTH_SERVICE_URL
    if path.startswith("/api/v1/admin/solicitudes"):
        return CREDIT_SERVICE_URL
    if path.startswith("/api/v1/admin/aportaciones"):
        return PAYMENT_SERVICE_URL
    if path.startswith("/api/v1/admin/dashboard") or path.startswith("/api/v1/admin/reportes"):
        return PORTAL_SERVICE_URL
    if path.startswith("/api/v1/portal/") and (
        path.endswith("/perfil") or path.endswith("/cuenta")
    ):
        return AUTH_SERVICE_URL
    if path.startswith("/api/v1/portal/"):
        return PORTAL_SERVICE_URL
    return None


async def _proxy(request: Request, base_url: str) -> Response:
    url = f"{base_url}{request.url.path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    body = await request.body()
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream = await client.request(
            request.method,
            url,
            content=body,
            headers=headers,
        )

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers={
            key: value
            for key, value in upstream.headers.items()
            if key.lower() not in {"content-encoding", "transfer-encoding", "content-length"}
        },
        media_type=upstream.headers.get("content-type"),
    )


@app.api_route("/api/v1/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_api(request: Request, full_path: str) -> Response:
    path = f"/api/v1/{full_path}"
    destino = _resolver_servicio(path, request.method)
    if not destino:
        return Response(content='{"detail":"Ruta no encontrada en gateway."}', status_code=404, media_type="application/json")
    return await _proxy(request, destino)


@app.get("/health")
async def health() -> dict:
    servicios = {
        "gateway": "ok",
        "auth-service": AUTH_SERVICE_URL,
        "credit-service": CREDIT_SERVICE_URL,
        "payment-service": PAYMENT_SERVICE_URL,
        "portal-service": PORTAL_SERVICE_URL,
    }
    estados: dict[str, str] = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for nombre, url in list(servicios.items())[1:]:
            try:
                resp = await client.get(f"{url}/health")
                estados[nombre] = "ok" if resp.status_code == 200 else "error"
            except httpx.HTTPError:
                estados[nombre] = "offline"
    return {"status": "ok", "servicio": "api-gateway", "microservicios": estados}
