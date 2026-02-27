"""Start the Adaptive Quiz backend server.

Usage:  python run.py
"""
from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    print("Starting Adaptive Quiz Backend...")
    print("API: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop.\n")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
