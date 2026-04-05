import os


class Config:
    """Base configuration for the Flask application."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
