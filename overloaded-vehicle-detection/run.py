# run.py
import os
import sys
import webbrowser
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import SERVER_HOST, SERVER_PORT
from my_utils.database import init_db
from webapp.server import app

def open_browser():
    time.sleep(1.5)
    url = f"http://localhost:{SERVER_PORT}"
    print(f"👉 Opening browser at: {url}")
    webbrowser.open(url)

def main():
    print("=" * 65)
    print("🚀 Starting Overload Guardian AI Traffic Enforcement System...")
    print("=" * 65)

    # Initialize Database
    init_db()

    # Automatically launch browser
    threading.Thread(target=open_browser, daemon=True).start()

    print(f"🌐 Dashboard & Live AI Stream active at http://localhost:{SERVER_PORT}")
    print("Press Ctrl+C to terminate the system.\n")

    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, threaded=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown complete.")
