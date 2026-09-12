"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_auth_service
from app.schemas.auth import LoginRequest, RegisterRequest, TokenRead, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
Service = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, service: Service):
    try:
        return service.register(payload.email, payload.password)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/login", response_model=TokenRead)
def login(payload: LoginRequest, service: Service):
    user = service.login(payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": service.token_for(user), "user": user}
