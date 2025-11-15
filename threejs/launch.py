"""
Quick launcher for Three.js visualization
Serves the project root so /data is accessible from the browser.
"""
import webbrowser
import http.server
import socketserver
import threading
import time
from pathlib import Path
import os
import functools
import subprocess

PORT = 8000

# Paths
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server():
    # Serve the project root so /data and /threejs are accessible
    Handler = functools.partial(QuietHTTPRequestHandler, directory=str(PROJECT_ROOT))
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":  
    print("=" * 60)
    print("THREE.JS NETWORK VISUALIZATION LAUNCHER")
    print("=" * 60)
    print()
    
    # Ensure data exists
    data_path = PROJECT_ROOT / "data" / "network_data.json"
    if not data_path.exists():
        print("network_data.json not found!")
        print("Running export script...")
        print()
        subprocess.run(["python", str(THIS_DIR / "export_data.py")], cwd=str(THIS_DIR))
        print()
    
    # Start server
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    
    # Open browser to the simple HTML (single-file solution)
    url = f"http://localhost:{PORT}/threejs/simple.html"
    print(f"Opening: {url}")
    print()
    print("Keep this window open")
    print("Press Ctrl+C to stop")
    print()
    print("=" * 60)
    
    webbrowser.open(url)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print("Done!")
