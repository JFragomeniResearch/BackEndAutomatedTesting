from typing import Any, List, Optional, Type, Union, Dict
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
        params: Dict = None
    ) -> List[Dict]:
        """Execute a database query and return results"""
        with self.beat.db_session() as session:
            result = session.execute(text(query), params or {})
            # Fix: Convert SQLAlchemy Row objects to dictionaries properly
            return [dict(zip(row.keys(), row)) for row in result]
    
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
        records: List[Dict]
    ) -> None:
        """Bulk insert records into a table"""
        with self.beat.db_session() as session:
            query = text(f"INSERT INTO {table} ({','.join(records[0].keys())}) VALUES ({','.join([':' + k for k in records[0].keys()])})")
            for record in records:
                session.execute(query, record)
    
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