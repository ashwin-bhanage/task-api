from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.security import decode_access_token
from typing import Optional

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Dependency to get current authenticated user from JWT cookie
    """
    # Get token from cookie
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Decode token
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Get user from database
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Optional authentication - returns None if not authenticated
    Useful for endpoints that work both authenticated and unauthenticated
    """
    token = request.cookies.get("access_token")

    if not token:
        return None

    payload = decode_access_token(token)

    if payload is None:
        return None

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user
