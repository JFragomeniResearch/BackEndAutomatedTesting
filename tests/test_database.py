import pytest
from beat import BEAT, TestConfig
from utils.database_helpers import DatabaseHelper

@pytest.fixture
def beat_framework():
    """Fixture to create BEAT instance with test configuration"""
    config = TestConfig(
        base_url="http://localhost:8000",
        db_url="sqlite:///test.db",
        api_key="test_token"
    )
    return BEAT(config)

@pytest.fixture
def db_helper(beat_framework):
    """Fixture to create DatabaseHelper instance"""
    return DatabaseHelper(beat_framework)

class TestDatabaseOperations:
    """Test suite for database operations"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db_helper):
        """Setup test data before each test"""
        # Create test table
        db_helper.execute_ddl("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        """)
        
        # Clean existing data
        db_helper.clear_table("users")
        
        # Insert test data
        test_users = [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"}
        ]
        db_helper.bulk_insert("users", test_users)
        
        yield
        
        # Cleanup after test
        db_helper.clear_table("users")

    def test_insert_and_verify_record(self, db_helper):
        """Test inserting a record and verifying its existence"""
        new_user = {
            "name": "Test User",
            "email": "test@example.com"
        }
        
        db_helper.insert_data("users", new_user)
        
        # Verify record exists
        assert db_helper.verify_record_exists("users", {
            "email": "test@example.com"
        })

    def test_query_results(self, db_helper):
        """Test querying and verifying results"""
        results = db_helper.execute_query(
            "SELECT * FROM users WHERE name = :name",
            {"name": "John Doe"}
        )
        
        assert len(results) == 1
        assert results[0]["name"] == "John Doe"
        assert results[0]["email"] == "john@example.com"

    def test_bulk_insert(self, db_helper):
        """Test bulk insertion of records"""
        # Clear the table first to ensure we start fresh
        db_helper.clear_table("users")
        
        new_users = [
            {"name": "User1", "email": "user1@example.com"},
            {"name": "User2", "email": "user2@example.com"},
            {"name": "User3", "email": "user3@example.com"}
        ]

        db_helper.bulk_insert("users", new_users)

        # Verify all records were inserted
        results = db_helper.execute_query("SELECT COUNT(*) as total FROM users")
        assert results[0]['total'] == len(new_users)

        # Optional: Verify the actual data
        all_users = db_helper.execute_query("SELECT name, email FROM users ORDER BY name")
        assert len(all_users) == len(new_users)
        for expected, actual in zip(new_users, all_users):
            assert expected['name'] == actual['name']
            assert expected['email'] == actual['email']

    def test_clear_table(self, db_helper):
        """Test clearing table data"""
        # Insert some test data first
        test_user = {"name": "Test User", "email": "test@example.com"}
        db_helper.execute_query(
            "INSERT INTO users (name, email) VALUES (:name, :email)",
            test_user
        )
        
        db_helper.clear_table("users")
        
        # Verify table is empty
        results = db_helper.execute_query("SELECT COUNT(*) as total FROM users")
        assert results[0]['total'] == 0
