"""
Database configuration and models using SQLAlchemy.

This module sets up the database connection and defines the data models for the application.
SQLAlchemy, an Object-Relational Mapper (ORM), is used to interact with the
database in a Pythonic way, abstracting away raw SQL queries.

The current configuration uses a local SQLite database (`test.db`) for development.
"""

from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # Later, for a production database, we change this

class Base(DeclarativeBase):
    """The base class for all SQLAlchemy models in the application."""
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    Represents a user in the database.

    Inherits from `SQLAlchemyBaseUserTableUUID` to get standard user fields
    (email, hashed_password, etc.) from `fastapi-users`.
    """
    # Defines the one-to-many relationship: one User can have many Posts.
    posts = relationship("Post", back_populates="user")
    

class Post(Base):
    """Represents a post made by a user in the database."""
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="Primary key for the post.")
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, comment="Foreign key linking to the user who created the post.") # One to many relationship(User has many posts)
    caption = Column(Text, comment="The text content of the post.")
    url = Column(String, nullable=False, comment="The URL of the uploaded media file on ImageKit.")
    file_type = Column(String, nullable=False, comment="The type of media file (e.g., 'image' or 'video').")
    file_name = Column(String, nullable=False, comment="The name of the file on ImageKit.")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Timestamp of when the post was created.")

    # Defines the many-to-one relationship: a Post belongs to one User.
    user = relationship("User", back_populates="posts")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    """Creates the database and all tables defined in the models.

    This function is called once at application startup to ensure the database
    schema is up to date with the models.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an async database session.

    This is a FastAPI dependency that creates and yields a new `AsyncSession`
    for each request, and ensures it's closed afterward.
    """
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the user database adapter for `fastapi-users`.

    This function provides `fastapi-users` with the necessary database adapter
    to interact with the `User` model.
    """
    yield SQLAlchemyUserDatabase(session, User)