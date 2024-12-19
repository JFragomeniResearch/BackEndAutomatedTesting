from typing import Any, List, Optional, Type, Union
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from beat import BEAT

class DatabaseHelper:
    """Helper class for database testing operations"""
    
    def __init__(self, beat_instance: BEAT):
        self.beat = beat_instance
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[dict] = None
    ) -> List[dict]:
        """Execute raw SQL query and return results"""
        with self.beat.db_session() as session:
            result = session.execute(text(query), params or {})
            return [dict(row) for row in result]
    
    def insert_data(
        self, 
        table: str, 
        data: dict
    ) -> None:
        """Insert single row of data into specified table"""
        query = f"INSERT INTO {table} ({','.join(data.keys())}) VALUES ({','.join([':' + k for k in data.keys()])})"
        with self.beat.db_session() as session:
            session.execute(text(query), data)
    
    def bulk_insert(
        self, 
        table: str, 
        data: List[dict]
    ) -> None:
        """Insert multiple rows of data into specified table"""
        if not data:
            return
            
        columns = data[0].keys()
        query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join([':' + k for k in columns])})"
        
        with self.beat.db_session() as session:
            for row in data:
                session.execute(text(query), row)
    
    def clear_table(
        self, 
        table: str
    ) -> None:
        """Delete all rows from specified table"""
        with self.beat.db_session() as session:
            session.execute(text(f"DELETE FROM {table}"))
    
    def verify_record_exists(
        self, 
        table: str, 
        conditions: dict
    ) -> bool:
        """Check if record exists matching given conditions"""
        where_clause = " AND ".join([f"{k} = :{k}" for k in conditions.keys()])
        query = f"SELECT COUNT(*) as count FROM {table} WHERE {where_clause}"
        
        with self.beat.db_session() as session:
            result = session.execute(text(query), conditions).first()
            return result.count > 0 