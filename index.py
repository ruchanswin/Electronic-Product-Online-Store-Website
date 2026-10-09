import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent / "awe_flask_app"
sys.path.insert(0, str(APP_DIR))

from app import app
