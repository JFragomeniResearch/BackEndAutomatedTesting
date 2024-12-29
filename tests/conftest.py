import pytest
from .mock_server import start_mock_server

@pytest.fixture(scope="session", autouse=True)
def mock_server():
    server = start_mock_server()
    yield server
    server.shutdown()
    server.server_close() 