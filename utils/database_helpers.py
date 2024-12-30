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
            
            # Check if the query is a SELECT statement
            if query.strip().upper().startswith('SELECT'):
                # Get column names from result
                columns = result.keys()
                # Convert each row to a dictionary using column names
                return [dict(zip(columns, row)) for row in result]
            
            # For non-SELECT queries (CREATE, INSERT, UPDATE, DELETE)
            return []
    
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
        if not records:
            return
        
        with self.beat.db_session() as session:
            columns = records[0].keys()
            placeholders = ','.join([':' + k for k in columns])
            column_names = ','.join(columns)
            query = text(f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})")
            
            for record in records:
                session.execute(query, record)
            session.commit()
    
    def clear_table(
        self, 
        table: str
    ) -> None:
        """Clear all records from a table"""
        with self.beat.db_session() as session:
            session.execute(text(f"DELETE FROM {table}"))
            session.commit()
    
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

    def execute_ddl(self, query: str) -> None:
        """Execute DDL statements (CREATE, ALTER, DROP)"""
        with self.beat.db_session() as session:
            session.execute(text(query))
            session.commit() 