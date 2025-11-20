"""
Simple HTTP Server for M4Markets Voice Agent
Serves the frontend web app locally for testing
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════╗
║         M4MARKETS VOICE AGENT - LOCAL SERVER            ║
╚══════════════════════════════════════════════════════════╝

✅ Server running at:

   http://localhost:{PORT}
   http://127.0.0.1:{PORT}

📁 Serving from: {DIRECTORY}

🌐 To test the app:
   1. Open: http://localhost:{PORT}/index.html?room=test&token=test
   2. Click "Unirse a la llamada"

⚠️  Note: You'll need valid room & token from LiveKit
   Use evolution_caller.py to generate them.

Press Ctrl+C to stop the server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped. Goodbye!")
