import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(dotenv_path=BASE_DIR / ".env")

ENGLISH_LEVELS = ("B1-B2", "C1-C2")
AGE = ("<16", "16-18", "19-24", ">24")

BACKEND_URL = os.getenv("BACKEND_URL", "https://api.ibratdebate.uz")

USERS_API_URL = BACKEND_URL + "/api/auth/users/"
REGIONS_API_URL = BACKEND_URL + "/api/auth/regions/"
DISTRICTS_API_URL = BACKEND_URL + "/api/auth/districts/"

DEBATES_API_URL = BACKEND_URL + "/api/core/debates/"
TICKETS_API_URL = BACKEND_URL + "/api/core/tickets/"


CHANNELS_IDs = {
    -1001825051597: ("Azizbek Zaylobiddinov", "https://t.me/abdulazizziy"),
    -1002277135189: ("Shoks", "https://t.me/shoks927"),
    -1002078049933: ("Akramjon Abdurakhimov", "https://t.me/akramjon_io"),
    # -1001803075478: ("Ozodbek Eshboboev", "https://t.me/ozodiiy"),
}
