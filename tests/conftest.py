import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, build_engine, get_db
from app.main import app


@pytest.fixture
def client():
    test_engine = build_engine("sqlite://")
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def book_payload():
    return {
        "title": "The Hobbit",
        "author": "J. R. R. Tolkien",
        "isbn": "9780547928227",
        "category": "Fantasy",
        "publisher": "Mariner Books",
        "published_year": 1937,
        "total_copies": 2,
    }


@pytest.fixture
def member_payload():
    return {
        "name": "Alex Reader",
        "email": "alex@example.com",
        "phone": "+1-555-0100",
        "address": "10 Library Lane",
        "membership_status": "Active",
    }
