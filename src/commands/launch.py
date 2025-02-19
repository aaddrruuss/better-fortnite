import base64
import aiohttp
from config import EPIC_PC_CLIENT_ID, EPIC_PC_CLIENT_SECRET, OAUTH_TOKEN_URL

async def getExchangeCode(access_token: str):
    url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/exchange"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                text_error = await resp.text()
                raise Exception(f"Error al obtener el exchange code: {resp.status} {text_error}")
            data = await resp.json()
    return data["code"]

async def exchange_code_for_token(exchange_code: str, client_id: str, client_secret: str) -> str:
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{client_id}:{client_secret}".encode()
        ).decode(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "exchange_code",
        "exchange_code": exchange_code,
        "token_type": "eg1"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(OAUTH_TOKEN_URL, headers=headers, data=data) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception(f"No se pudo obtener token PC: {resp.status} => {resp_json}")
            return resp_json["access_token"]

async def get_pc_exchange_code(switch_access_token: str) -> str:
    user_exchange = await getExchangeCode(switch_access_token)
    pc_token = await exchange_code_for_token(
        user_exchange,
        EPIC_PC_CLIENT_ID,
        EPIC_PC_CLIENT_SECRET
    )
    pc_exchange_code = await getExchangeCode(pc_token)
    return pc_exchange_code

async def play_fortnite(switch_access_token: str, account_id: str, fortnite_dir: str) -> str:
    pc_exchange_code = await get_pc_exchange_code(switch_access_token)
    launch_link = (
        f'start /d "{fortnite_dir}" '
        'FortniteLauncher.exe '
        '-AUTH_LOGIN=unused '
        f'-AUTH_PASSWORD={pc_exchange_code} '
        '-AUTH_TYPE=exchangecode '
        '-epicapp=Fortnite -epicenv=Prod '
        '-EpicPortal '
        f'-epicuserid={account_id}'
    )
    return launch_link
