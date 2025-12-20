#!/usr/bin/env python3
"""
Local development server for portfolio site.
Runs on localhost:5555
"""
import http.server
import socketserver
import sys
from pathlib import Path

PORT = 5555
DIRECTORY = Path(__file__).parent.parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

def main():
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🚀 Server running at http://localhost:{PORT}/")
            print(f"📁 Serving directory: {DIRECTORY}")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use")
            print(f"   Try: lsof -ti:{PORT} | xargs kill")
            sys.exit(1)
        else:
            raise

if __name__ == "__main__":
    main()
