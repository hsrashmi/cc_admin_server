from fastapi import Depends, FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.config import API_PREFIX, ALLOWED_HOSTS
from src.database import AsyncSessionLocal, Base, engine
from src.dependencies import get_token_header
from src.routers.api import router as router_api
from src.routers.handlers.http_error import http_error_handler
from logger import logger
import asyncio

def get_application() -> FastAPI:
    """Configure, start, and return the application."""
    
    # Logging
    logger.info("Starting application")

    # Start FastAPI App
    application = FastAPI()

    # Allow CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mapping API routes
    application.include_router(router_api, prefix=API_PREFIX)

    # Add exception handlers
    application.add_exception_handler(HTTPException, http_error_handler)

    return application

app = get_application()

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await create_tables()  # Ensures tables are created at app startup

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middleware to attach a database session to each request."""
    response = Response("Internal server error", status_code=500)
    try:
        async with AsyncSessionLocal() as session:
            request.state.db = session
            response = await call_next(request)
    finally:
        await request.state.db.close()  # Ensure async session is properly closed
    return response
