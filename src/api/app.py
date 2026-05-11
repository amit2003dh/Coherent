"""
API entry point for deployment compatibility.
This file imports the app from main.py to support both local and cloud deployments.
"""
from .main import app

# Export app for direct import
__all__ = ['app']
