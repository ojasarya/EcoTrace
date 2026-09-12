"""Helpers for safe SQLAlchemy transaction boundaries."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def commit_or_rollback(session: Session) -> None:
    """Commit a unit of work and restore the session if the commit fails."""

    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
