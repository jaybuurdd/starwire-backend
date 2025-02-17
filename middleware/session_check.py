from utils.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request


def check_user_session(request: Request, db: Session = Depends(get_db)) -> bool:
    """
        Middleware to validate session token and retrieve the authenticated user.
    """

    session_token = request.cookies.get("session_token")

    # check authorization header exists
    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="Missing session token."
        )
    
    # retrieve session from db
    session = db.query(Session).filter(Session.data.contains(session_token)).first()

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid session token."
        )
    
    # check if session expired
    current_time = datetime.now(timezone.utc)
    if session.expires < current_time:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please sign in again"
        )
    
    return True