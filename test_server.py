#!/usr/bin/env python3
import http.server
import socketserver
import os

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

PORT = 8000
os.chdir('/Users/kylexu/JCL_AT_Buddy')

with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    print("Cache disabled - you'll always get the latest files!")
    httpd.serve_forever()
