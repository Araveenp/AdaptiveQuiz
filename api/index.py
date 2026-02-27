"""Vercel serverless function entry point for the Flask backend."""
import sys
import os

# Add project root to path so backend package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app

app = create_app()
