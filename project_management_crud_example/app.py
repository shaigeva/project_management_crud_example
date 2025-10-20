"""FastAPI application for project management backend service.

This module sets up the main FastAPI application with database initialization,
CORS middleware, dependency injection, and core endpoints.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from project_management_crud_example.dependencies import get_database
from project_management_crud_example.routers import health, stub_entity_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifespan events."""
    # Initialize database on startup
    logger.info("Initializing database")
    db = get_database()
    db.create_tables()
    yield
    # Cleanup resources on shutdown if needed
    pass


app = FastAPI(
    title="Project Management API",
    description="Backend service with stub entity template/scaffolding built with FastAPI and SQLite",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stub_entity_api.router)
app.include_router(health.router)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with detailed error information."""
    logger.warning(f"Validation error on {request.method} {request.url}: {exc.errors()}")

    # Convert the errors to a JSON-serializable format
    errors = []
    for error in exc.errors():
        # Ensure all values are JSON serializable
        json_error = {}
        for key, value in error.items():
            if isinstance(value, bytes):
                # Convert bytes to string representation
                json_error[key] = value.decode("utf-8", errors="replace")
            else:
                json_error[key] = value
        errors.append(json_error)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent error format."""
    logger.warning(f"HTTP error on {request.method} {request.url}: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with generic error response."""
    logger.error(f"Unexpected error on {request.method} {request.url}: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
