#!/usr/bin/env python3
"""
Simple HTTP server to serve Allure Report
Usage: python serve_report.py [port]
Default port: 8080
"""
import http.server
import socketserver
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
DIRECTORY = "reports/allure-html"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"\n🚀 Allure Report Server Started!")
    print(f"=" * 50)
    print(f"📊 Report URL: http://localhost:{PORT}")
    print(f"=" * 50)
    print(f"\nPress Ctrl+C to stop the server\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped.")
