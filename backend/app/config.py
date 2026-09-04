import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# FreeLLMAPI Configuration
FREELLMAPI_API_KEY = os.getenv("FREELLMAPI_API_KEY")
FREELLMAPI_BASE_URL = os.getenv("FREELLMAPI_BASE_URL", "http://127.0.0.1:31415/v1")
FREELLMAPI_MODEL = os.getenv("FREELLMAPI_MODEL", "auto")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./settlelens.db")

# Backend Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))

# Frontend Configuration (for reference, not used in backend)
FRONTEND_HOST = os.getenv("FRONTEND_HOST", "localhost")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", 5173))