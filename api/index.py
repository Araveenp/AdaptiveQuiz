"""Vercel serverless function entry point for the Flask backend."""
import sys
import os

# Add project root to path so backend package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set VERCEL env var if not already set (Vercel sets this automatically,
# but be explicit for our config detection)
os.environ.setdefault("VERCEL", "1")

from backend.app import create_app

app = create_app()

# Vercel expects an `app` variable (WSGI) or a `handler` function
# The @vercel/python builder picks up the `app` WSGI application automatically
