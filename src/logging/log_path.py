
# Define the project root and logs directory
from pathlib import Path


LOGS_DIR = Path("data/log")
# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)
