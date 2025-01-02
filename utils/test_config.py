from dataclasses import dataclass

@dataclass
class TestConfig:
    """Test configuration class"""
    api_key: str
    base_url: str
    db_url: str = "sqlite:///test.db"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0 