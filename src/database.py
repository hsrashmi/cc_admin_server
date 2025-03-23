import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from starlette.config import Config

config = Config(".env")  # Automatically loads variables from .env file

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:careercompass@172.28.208.1:5432/careercompass"

engine = create_async_engine(
    url=config("DB_URL", default=SQLALCHEMY_DATABASE_URL),    
    echo=True,
    pool_size=10,  # Max persistent connections
    max_overflow=5,  # Additional temporary connections if needed
    pool_timeout=30  # Max wait time for a connection
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Define Base for ORM models
class Base(DeclarativeBase):
    pass
