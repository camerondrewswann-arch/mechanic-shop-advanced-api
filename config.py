import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development-jwt-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "24"))

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///mechanic_shop.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "60"))

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = ["200 per day", "50 per hour"]
    RATELIMIT_HEADERS_ENABLED = True


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CACHE_TYPE = "SimpleCache"
    RATELIMIT_ENABLED = False
    WTF_CSRF_ENABLED = False
