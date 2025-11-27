import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


class Config:
    """Base Configuration with validation."""

    def __init__(self):
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.name = os.getenv('DB_NAME')
        self.charset = os.getenv('DB_CHARSET', 'utf8mb4')

        # Flask defaults
        self.DEBUG = False
        self.TESTING = False
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')

        # Brutal validation: Die if vars are missing
        if not all([self.user, self.host, self.name]):
            print(self.user, self.host, self.name)
            print("[CONFIG ERROR] Missing critical DB environment variables.")
            sys.exit(1)

    @property
    def database_url(self):
        """Constructs the connection string dynamically."""
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}?charset={self.charset}"
        )


class TestConfig(Config):
    """Testing Configuration to fix ImportError."""

    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.DEBUG = True


class DatabaseConnector:
    """Simple Fail-Fast Connector."""

    def __init__(self, config):
        self.config = config

    def connect(self):
        """Attempts connection. Exits app on failure."""
        print(f"Checking database connection to: {self.config.host}...")
        try:
            # Short timeout to avoid hanging
            engine = create_engine(
                self.config.database_url,
                connect_args={'connect_timeout': 5}
            )
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                print("[SUCCESS] Database is reachable.")
                return True
        except Exception as e:
            print(f"[CRITICAL] Database connection failed: {e}")
            sys.exit(1)