import logging
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from contextlib import contextmanager

@dataclass
class TestConfig:
    """Test configuration class"""
    base_url: str = "https://jsonplaceholder.typicode.com"  # Example test API
    db_url: str = "sqlite:///test.db"
    api_key: str = "test_token"
    timeout: int = 30
    max_retries: int = 3

class BEAT:
    """Backend Automated Testing Framework"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.db_engine = create_engine(config.db_url)
        self.session = None
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the test framework"""
        logger = logging.getLogger('BEAT')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @contextmanager
    def db_session(self):
        """Database session context manager"""
        session = Session(self.db_engine)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def api_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Execute API request with retry logic"""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {}
        
        if self.config.api_key:
            headers['Authorization'] = f"Bearer {self.config.api_key}"
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=self.config.timeout
                )
                return response
                
            except requests.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.config.max_retries - 1:
                    raise
