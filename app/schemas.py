"""
Pydantic Schemas for API Data Validation and Serialization.

This module defines the Pydantic models (schemas) that FastAPI uses to:
- Validate incoming request data (e.g., for creating a user).
- Serialize outgoing response data (e.g., when returning user information).
- Automatically generate OpenAPI (Swagger) documentation.
"""

from pydantic import BaseModel
from fastapi_users import schemas
import uuid


class PostCreate(BaseModel):
    """Schema for creating a new post.

    Note: This schema appears to be from a previous version of the application.
    The current post creation logic in `app.py` uses `caption` from a form,
    not `title` and `content` from a JSON body.
    """
    title: str
    content: str


class PostResponse(BaseModel):
    """Schema for returning a post in a response.

    Note: This schema is currently unused. The `/feed` endpoint returns a custom
    dictionary structure, not this Pydantic model.
    """
    title: str
    content: str


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for reading user data. Used in API responses.

    This determines which user fields are returned to the client. It safely
    excludes sensitive data like `hashed_password`.
    """
    pass


class UserCreate(schemas.BaseUserCreate):
    """Schema for user registration. Used for request bodies.

    This defines the fields required to create a new user, typically `email`
    and `password`.
    """
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data. Used for request bodies.

    This defines the fields that a user is allowed to update.
    """
    pass