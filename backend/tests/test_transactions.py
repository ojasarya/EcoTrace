from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.db.transactions import commit_or_rollback


def test_commit_or_rollback_restores_session_after_database_error() -> None:
    session = Mock()
    session.commit.side_effect = SQLAlchemyError("database failure")

    with pytest.raises(SQLAlchemyError, match="database failure"):
        commit_or_rollback(session)

    session.rollback.assert_called_once_with()
