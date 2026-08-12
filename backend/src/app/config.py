import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parent.parent.parent / "data"))

JWT_SECRET = "o-suivi-dev-secret"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 12

