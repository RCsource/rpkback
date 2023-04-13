import os
from pathlib import Path
import dotenv

dotenv.load_dotenv()


# auth configuration
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7)

# database configuration
DB_USER = os.environ["DB_USER"]
DB_PSWD = os.environ["DB_PSWD"]
DB_NAME = os.environ["DB_NAME"]
DB_PORT = os.environ.get("DB_PORT", 5432)
DB_HOST = os.environ.get("DB_HOST", "localhost")


ROOT_DIR = Path(__file__).parent.parent

YANDEX_TOKEN = os.environ["YANDEX_TOKEN"]
