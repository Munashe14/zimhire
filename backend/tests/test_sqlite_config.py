from app.core.config import settings


def test_database_url_uses_sqlite():
    assert "sqlite" in settings.DATABASE_URL.lower()
