from app.core.config import Settings


def test_config_defaults():
    s = Settings(
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DATABASE="certificate_test"
    )
    assert s.API_V1_PREFIX == "/api/v1"
    assert s.JWT_ALGORITHM == "HS256"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert s.REFRESH_TOKEN_EXPIRE_DAYS > 0


def test_cors_parsing():
    # Test JSON string parsing
    s1 = Settings(CORS_ORIGINS='["http://example.com", "http://localhost:3000"]')
    assert "http://example.com" in s1.CORS_ORIGINS
    assert "http://localhost:3000" in s1.CORS_ORIGINS

    # Test comma-separated string parsing
    s2 = Settings(CORS_ORIGINS="http://alpha.com, http://beta.com")
    assert "http://alpha.com" in s2.CORS_ORIGINS
    assert "http://beta.com" in s2.CORS_ORIGINS
