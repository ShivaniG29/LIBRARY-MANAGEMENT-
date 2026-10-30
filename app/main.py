import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import models  # noqa: F401 - register ORM models before create_all
from app.api.routes import book_routes, dashboard_routes, issue_routes, member_routes, return_routes
from app.core.config import settings
from app.database.database import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="REST API for managing library books, members, loans, returns, and statistics.",
    lifespan=lifespan,
)

for route in (
    book_routes.router,
    member_routes.router,
    issue_routes.router,
    return_routes.router,
    dashboard_routes.router,
):
    app.include_router(route, prefix="/api/v1")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={"error": {"code": f"HTTP_{exc.status_code}", "message": message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    details = [
        {"location": error["loc"], "message": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed.",
            "details": details,
        }},
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled application error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}},
    )


@app.get("/", tags=["Health"], summary="Health check")
def health_check():
    return {"status": "ok", "docs": "/docs"}
