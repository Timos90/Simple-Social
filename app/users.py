"""
User Authentication Configuration using `fastapi-users`.

This module sets up everything needed for user authentication, including:
- A `UserManager` to handle the business logic of users (creation, passwords).
- A JWT strategy for creating and verifying JSON Web Tokens.
- An authentication backend that combines the transport (Bearer tokens) and the JWT strategy.
- The main `FastAPIUsers` instance, which provides the authentication routers.
- A dependency (`current_active_user`) to protect endpoints.
"""

import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User, get_user_db
import os

SECRET = os.getenv("JWT_SECRET")

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Manages user-related operations like registration, password hashing, etc."""
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Hook called after a user is successfully registered."""
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        """Hook called after a user has requested a password reset."""
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        """Hook called after a user has requested email verification."""
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """FastAPI dependency to get the user manager."""
    yield UserManager(user_db)

# Defines how the client will send the token (in this case, via an Authorization header with a Bearer token).
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    """Configures the JWT strategy for creating and validating tokens."""
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

# The authentication backend, which combines the transport (how tokens are sent)
# and the strategy (how tokens are generated and verified).
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# The main `fastapi-users` instance. This is used to generate the auth routers.
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Dependency to get the current authenticated and active user.
# This is used to protect endpoints that require a logged-in user.
current_active_user = fastapi_users.current_user(active=True)
    