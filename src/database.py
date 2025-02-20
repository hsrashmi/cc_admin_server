import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.config import Config

config = Config(".env")  # Automatically loads variables from .env file
###
# Database Configuration
###

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:careercompass@172.28.208.1:5432/ilp"

engine = create_engine(
    config("DB_URL", default=SQLALCHEMY_DATABASE_URL)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
