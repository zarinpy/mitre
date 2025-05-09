import uvicorn
from fastapi import FastAPI

from routers import routes

app = FastAPI(
    title="Headless CMS",
    description=(
        "A lightweight CMS backend with Users, Roles, Permissions,"
        " Content Management, Taxonomies, and Menus."
    ),
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.include_router(routes)


def main() -> None:
    """Run the FastAPI app with Uvicorn."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        # Use 8000 for dev; use 80/443 behind a proxy (e.g., nginx) in prod
        port=8000,
        # Auto-reload in dev mode
        reload=True,
        # Number of workers, increase for production (ex: workers=4)
        workers=1,
        # Trust proxy headers (useful when behind nginx)
        proxy_headers=True,
        # Allow forwarded IPs
        forwarded_allow_ips="*",
        # Good default
        log_level="info",
    )


if __name__ == "__main__":
    main()
