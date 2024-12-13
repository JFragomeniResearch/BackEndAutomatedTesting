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
    """Configuration class for the testing framework"""
    api_base_url: str
    db_connection_string: str
    auth_token: Optional[str] = None
    retry_attempts: int = 3
    timeout: int = 30
    environment: str = "test"

class BEAT:
    """Backend Automated Testing Framework"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.db_engine = create_engine(config.db_connection_string)
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
        url = f"{self.config.api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {}
        
        if self.config.auth_token:
            headers['Authorization'] = f"Bearer {self.config.auth_token}"
        
        for attempt in range(self.config.retry_attempts):
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
                if attempt == self.config.retry_attempts - 1:
                    raise
