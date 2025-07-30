import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

LOGIN_URL: str = os.getenv('LOGIN_URL')
RECORDS_URL: str = os.getenv('RECORDS_URL')
EXPECTED_POST_LOGIN_URL: str = os.getenv('EXPECTED_POST_LOGIN_URL')
TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', '10'))