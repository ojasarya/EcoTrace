"""User registration, password verification, and JWT authentication."""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.user import User

password_hash = PasswordHash.recommended()


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def register(self, email: str, password: str) -> User:
        normalized = email.casefold()
        if self.session.scalar(select(User).where(User.email == normalized)) is not None:
            raise ValueError("Email is already registered")
        user = User(email=normalized, password_hash=password_hash.hash(password))
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def login(self, email: str, password: str) -> User | None:
        user = self.session.scalar(select(User).where(User.email == email.casefold()))
        if user is None or not user.is_active or not password_hash.verify(
            password, user.password_hash
        ):
            return None
        return user

    @staticmethod
    def token_for(user: User) -> str:
        settings = get_settings()
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_expiration_minutes
        )
        return jwt.encode(
            {"sub": str(user.id), "email": user.email, "exp": expires},
            settings.jwt_secret,
            algorithm="HS256",
        )
