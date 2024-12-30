from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import pytest

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/users/1":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "id": 1,
                "name": "Test User",
                "email": "test@example.com",
                "address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "zipcode": "12345"
                }
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/users/999":
            self.send_response(404)
            self.end_headers()
        elif self.path.startswith("/users/invalid"):
            self.send_response(400)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/users":
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "id": 2,
                "name": post_data["name"],
                "email": post_data["email"]
            }
            self.wfile.write(json.dumps(response).encode())

def start_mock_server():
    server = HTTPServer(('localhost', 8000), MockHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return server

@pytest.fixture(scope="session", autouse=True)
def mock_server():
    server = start_mock_server()
    yield server
    server.shutdown()
    server.server_close() 