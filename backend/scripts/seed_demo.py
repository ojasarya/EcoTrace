"""Seed the local database with a complete EcoTrace demo dataset."""

from app.db.session import get_session_factory
from app.services.demo_seed_service import seed_demo_data


def main() -> None:
    session = get_session_factory()()
    try:
        factory = seed_demo_data(session)
        print(f"Demo data available for factory {factory.id}: {factory.name}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
