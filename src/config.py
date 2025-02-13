import os
from dotenv import load_dotenv

load_dotenv()

EPIC_CLIENT_ID_SWITCH = os.getenv("EPIC_CLIENT_ID_SWITCH")
EPIC_CLIENT_SECRET_SWITCH = os.getenv("EPIC_CLIENT_SECRET_SWITCH")
EPIC_PC_CLIENT_ID = os.getenv("EPIC_PC_CLIENT_ID")
EPIC_PC_CLIENT_SECRET = os.getenv("EPIC_PC_CLIENT_SECRET")

OAUTH_TOKEN_URL = "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token"
DEVICE_CODE_URL = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/deviceAuthorization"
