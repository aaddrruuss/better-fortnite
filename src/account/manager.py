import json
import glob
import re
import os
import webbrowser
import asyncio
from auth.auth import get_client_credentials_token, create_device_code, poll_for_token, create_device_auth

async def authenticate(filename: str) -> dict:
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            if all(k in data for k in ("account_id", "deviceId", "secret")):
                print(f"[*] Datos de {filename} cargados.")
                return data
        except:
            pass
    print(f"[*] No se encontraron datos en {filename}. Iniciando proceso de autenticación.")
    client_token = await get_client_credentials_token()
    device_code_response = await create_device_code(client_token)
    device_code = device_code_response["device_code"]
    verification_url = device_code_response["verification_uri_complete"]
    webbrowser.open(verification_url)
    print(f"[!] Por favor, ve a este enlace para completar el login: {verification_url}")
    token_data = await poll_for_token(device_code, device_code_response["interval"])
    account_id = token_data["account_id"]
    access_token = token_data["access_token"]
    device_auth = await create_device_auth(access_token, account_id)
    data = {
        "account_id": account_id,
        "deviceId": device_auth["deviceId"],
        "secret": device_auth["secret"]
    }
    with open(filename, 'w') as f:
        json.dump(data, f)
    print(f"[+] Autenticación completada y datos guardados en {filename}")
    return data

def load_all_accounts():
    account_files = glob.glob("device_auths*.json")
    def sort_key(fname):
        m = re.search(r"device_auths(\d+)\.json", fname)
        return int(m.group(1)) if m else 0
    account_files.sort(key=sort_key)
    accounts = []
    for fname in account_files:
        try:
            with open(fname, "r") as f:
                data = json.load(f)
                if all(k in data for k in ("account_id", "deviceId", "secret")):
                    accounts.append((fname, data))
        except Exception as e:
            print(f"[!] Error al cargar {fname}: {e}")
    return accounts

async def get_display_name_for_account(device_auth_data: dict) -> str:
    try:
        from commands.refresh import refresh_access_token
        token = await refresh_access_token(device_auth_data)
        account_id = device_auth_data["account_id"]
        url = f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{account_id}"
        import aiohttp
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return "Desconocido"
                data = await resp.json()
                return data.get("displayName", "Sin nombre")
    except Exception as ex:
        return f"Error: {ex}"
