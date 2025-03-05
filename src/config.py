import os
from dotenv import load_dotenv

load_dotenv()

EPIC_PC_CLIENT_ID="34a02cf8f4414e29b15921876da36f9a"
EPIC_PC_CLIENT_SECRET="daafbccc737745039dffe53d94fc76cf"
EPIC_CLIENT_ID_SWITCH="98f7e42c2e3a4f86a74eb43fbb41ed39"
EPIC_CLIENT_SECRET_SWITCH="0a2449a2-001a-451e-afec-3e812901c4d7"

OAUTH_TOKEN_URL = "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token"
DEVICE_CODE_URL = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/deviceAuthorization"

display_names = []

FORTNITE_DIR = "C:\\Program Files\\Epic Games\\Fortnite\\FortniteGame\\Binaries\\Win64"