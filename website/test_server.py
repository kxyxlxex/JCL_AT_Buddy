#!/usr/bin/env python3
"""
Simple HTTP server for testing the JCL Test Generator website locally.
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler that adds no-cache headers to all responses."""
    
    def end_headers(self):
        # Add no-cache headers
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def start_test_server(port=8000):
    """Start a local HTTP server for testing the website."""
    
    # Change to the website directory
    website_dir = Path(__file__).parent
    os.chdir(website_dir)
    
    # Create the server with no-cache handler
    handler = NoCacheHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Starting test server on port {port}")
        print(f"Serving files from: {website_dir}")
        print(f"Open your browser to: http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Try to open the browser automatically
        try:
            webbrowser.open(f'http://localhost:{port}')
        except:
            print("Could not open browser automatically")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            httpd.shutdown()

if __name__ == "__main__":
    start_test_server()
