"""
Simple HTTP server to serve static HTML files.
This is a fallback option if Streamlit is not working.
"""

import http.server
import socketserver
import os
import sys

# Default port
PORT = 8000

# Try to get port from command line arguments
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        print(f"Invalid port number: {sys.argv[1]}. Using default port {PORT}.")

# Set the directory to serve files from
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        print(f"{self.client_address[0]} - {format % args}")

def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"To view the test page, open a browser and navigate to http://localhost:{PORT}/index.html")
        print("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
