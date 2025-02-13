import os
import json
import time
import base64
import asyncio
import aiohttp
import webbrowser
import threading
import keyboard
import glob
import re
import subprocess
from dotenv import load_dotenv
import tkinter as tk

load_dotenv()

# ---------------------------------------------------
# Constantes y URLs
# ---------------------------------------------------
EPIC_CLIENT_ID_SWITCH = os.getenv("EPIC_CLIENT_ID_SWITCH")
EPIC_CLIENT_SECRET_SWITCH = os.getenv("EPIC_CLIENT_SECRET_SWITCH")
EPIC_PC_CLIENT_ID = os.getenv("EPIC_PC_CLIENT_ID")
EPIC_PC_CLIENT_SECRET = os.getenv("EPIC_PC_CLIENT_SECRET")

OAUTH_TOKEN_URL = "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token"
DEVICE_CODE_URL = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/deviceAuthorization"

# ---------------------------------------------------
# Funciones de autenticación
# ---------------------------------------------------
async def get_client_credentials_token():
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{EPIC_CLIENT_ID_SWITCH}:{EPIC_CLIENT_SECRET_SWITCH}".encode()
        ).decode(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    async with aiohttp.ClientSession() as session:
        async with session.post(OAUTH_TOKEN_URL, headers=headers, data=data) as resp:
            resp_json = await resp.json()
            if resp.status == 200:
                return resp_json["access_token"]
            else:
                error_text = await resp.text()
                raise Exception(f"Error obtaining client_credentials token: {resp.status} {error_text}")

async def create_device_code(bearer_token: str):
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"scope": "basic_profile friends_list"}
    async with aiohttp.ClientSession() as session:
        async with session.post(DEVICE_CODE_URL, headers=headers, data=data) as resp:
            resp_json = await resp.json()
            if resp.status == 200:
                return resp_json
            else:
                raise Exception(f"Error creating device code: {resp.status}")

async def poll_for_token(device_code: str, interval: int):
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{EPIC_CLIENT_ID_SWITCH}:{EPIC_CLIENT_SECRET_SWITCH}".encode()
        ).decode(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "device_code",
        "device_code": device_code,
        "token_type": "eg1"
    }
    max_wait_seconds = 300  # 5 minutos
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        while True:
            if time.time() - start_time > max_wait_seconds:
                raise Exception("Time limit exceeded during token polling")
            async with session.post(OAUTH_TOKEN_URL, headers=headers, data=data) as resp:
                if resp.status == 200:
                    return await resp.json()
                text_data = await resp.text()
                try:
                    error_json = await resp.json()
                except:
                    error_json = {}
                error_code = error_json.get("errorCode", "").lower()
                if "authorization_pending" in error_code or resp.status == 418:
                    await asyncio.sleep(interval)
                    continue
                raise Exception(f"Error polling token: {resp.status} {text_data}")

async def new_token(deviceId: str, account_id: str, secret: str):
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{EPIC_CLIENT_ID_SWITCH}:{EPIC_CLIENT_SECRET_SWITCH}".encode()
        ).decode(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "device_auth",
        "device_id": deviceId,
        "account_id": account_id,
        "secret": secret,
        "token_type": "eg1"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(OAUTH_TOKEN_URL, headers=headers, data=data) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception(f"Unexpected error {resp.status}")
            return resp_json

async def create_device_auth(access_token: str, account_id: str):
    url = f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{account_id}/deviceAuth"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Unexpected error creating device auth: {resp.status}")
            return await resp.json()

# ---------------------------------------------------
# Funciones de comandos (Party y STW)
# ---------------------------------------------------
async def leaveParty(access_token: str, party_id: str, account_id: str) -> bool:
    url = f"https://party-service-prod.ol.epicgames.com/party/api/v1/Fortnite/parties/{party_id}/members/{account_id}"
    headers = {"Authorization": f"bearer {access_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as resp:
            if resp.status not in (204, 200):
                text_error = await resp.text()
                raise Exception(f"Error leaving party: {resp.status} {text_error}")
    return True

async def getPartyId(access_token: str, account_id: str):
    url = f"https://party-service-prod.ol.epicgames.com/party/api/v1/Fortnite/user/{account_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise Exception(f"Error getting partyID: {resp.status}")
    return data["current"][0]["id"]

async def OpenCardPackBatch(access_token: str, account_id: str):
    query_url = (
        f"https://fortnite-public-service-prod11.ol.epicgames.com"
        f"/fortnite/api/game/v2/profile/{account_id}/client/QueryProfile?profileId=campaign"
    )
    open_url = (
        f"https://fngw-mcp-gc-livefn.ol.epicgames.com"
        f"/fortnite/api/game/v2/profile/{account_id}/client/OpenCardPackBatch"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(query_url, headers=headers, json={}) as data_resp:
            data = await data_resp.json()
            if data_resp.status != 200:
                raise Exception(f"Error en QueryProfile STW: {data_resp.status} {data}")
        rvn = data["profileChanges"][0]["profile"]["rvn"]
        items = data["profileChanges"][0]["profile"]["items"]
        rewards_guids = [guid for guid, details in items.items() if details.get("templateId", "").startswith("CardPack:")]
        if not rewards_guids:
            return
        params = {"profileId": "campaign", "rvn": rvn}
        payload = {"cardPackItemIds": rewards_guids}
        async with session.post(open_url, headers=headers, params=params, json=payload) as resp:
            if resp.status not in (200, 500):
                text_error = await resp.text()
                raise Exception(f"Error al abrir paquetes: {resp.status} {text_error}")
    return True

async def claimMissionAlertRewards(access_token: str, account_id: str):
    query_url = (
        f"https://fortnite-public-service-prod11.ol.epicgames.com"
        f"/fortnite/api/game/v2/profile/{account_id}/client/QueryProfile?profileId=campaign"
    )
    claim_url = (
        f"https://fortnite-public-service-prod11.ol.epicgames.com"
        f"/fortnite/api/game/v2/profile/{account_id}/client/ClaimMissionAlertRewards"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(query_url, headers=headers, json={}) as data_resp:
            data = await data_resp.json()
            if data_resp.status != 200:
                raise Exception(f"Error en QueryProfile STW: {data_resp.status} {data}")
        rvn = data["profileChanges"][0]["profile"]["rvn"]
        params = {"profileId": "campaign", "rvn": rvn}
        async with session.post(claim_url, headers=headers, params=params, json={}) as resp:
            if resp.status not in (200, 204):
                text_error = await resp.text()
                raise Exception(f"Error al reclamar las recompensas: {resp.status} {text_error}")
    return True

async def claimQuestRewards(access_token: str, account_id: str):
    query_url = (
        f"https://fortnite-public-service-prod11.ol.epicgames.com"
        f"/fortnite/api/game/v2/profile/{account_id}/client/QueryProfile?profileId=campaign"
    )
    claim_url = (
        f"https://fngw-mcp-gc-livefn.ol.epicgames.com"
        f"/fortnite/api/game/v2/profile/{account_id}/client/ClaimQuestReward"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(query_url, headers=headers, json={}) as data_resp:
            data = await data_resp.json()
            if data_resp.status != 200:
                raise Exception(f"Error en QueryProfile STW: {data_resp.status} {data}")
        rvn = data["profileChanges"][0]["profile"]["rvn"]
        items = data["profileChanges"][0]["profile"]["items"]
        completed_quest_guid = None
        for guid, details in items.items():
            template_id = details.get("templateId", "")
            attributes = details.get("attributes", {})
            if template_id.startswith("Quest:") and attributes.get("quest_state") == "Completed":
                completed_quest_guid = guid
                break
        if completed_quest_guid is None:
            return
        params = {"profileId": "campaign", "rvn": rvn}
        payload = {"questId": completed_quest_guid, "selectedRewardIndex": 0}
        async with session.post(claim_url, headers=headers, params=params, json=payload) as resp:
            if resp.status != 200:
                text_error = await resp.text()
                raise Exception(f"Error al reclamar la recompensa de la misión: {resp.status} {text_error}")
    return True

# ---------------------------------------------------
# Funciones para lanzar Fortnite en PC
# ---------------------------------------------------
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

async def play_fortnite(switch_access_token: str, account_id: str) -> str:
    pc_exchange_code = await get_pc_exchange_code(switch_access_token)
    launch_link = (
        'start /d "C:\\Program Files\\Epic Games\\Fortnite\\FortniteGame\\Binaries\\Win64" '
        'FortniteLauncher.exe '
        '-AUTH_LOGIN=unused '
        f'-AUTH_PASSWORD={pc_exchange_code} '
        '-AUTH_TYPE=exchangecode '
        '-epicapp=Fortnite -epicenv=Prod '
        '-EpicPortal '
        f'-epicuserid={account_id}'
    )
    return launch_link

# ---------------------------------------------------
# Funciones para refrescar token y ejecutar comandos
# ---------------------------------------------------
async def refresh_access_token(device_auth_data: dict) -> str:
    token_data = await new_token(
        device_auth_data["deviceId"],
        device_auth_data["account_id"],
        device_auth_data["secret"]
    )
    return token_data["access_token"]

async def command_leave_party(device_auth_data: dict):
    try:
        print("[*] Ejecutando comando: Leave Party")
        access_token = await refresh_access_token(device_auth_data)
        account_id = device_auth_data["account_id"]
        party_id = await getPartyId(access_token, account_id)
        await leaveParty(access_token, party_id, account_id)
        print("[+] Has abandonado la party correctamente.")
    except Exception as e:
        print("[!] Error en leave party:", str(e))

async def command_skip(device_auth_data: dict):
    try:
        print("[*] Ejecutando comando: Skip")
        access_token = await refresh_access_token(device_auth_data)
        account_id = device_auth_data["account_id"]
        party_id = await getPartyId(access_token, account_id)
        await leaveParty(access_token, party_id, account_id)
        await OpenCardPackBatch(access_token, account_id)
        await claimMissionAlertRewards(access_token, account_id)
        for _ in range(6):
            await claimQuestRewards(access_token, account_id)
        print("[+] Comando skip ejecutado correctamente.")
    except Exception as e:
        print("[!] Error en skip:", str(e))

async def command_play_fortnite(device_auth_data: dict):
    try:
        print("[*] Ejecutando comando: Play Fortnite")
        # Se verifica en un bucle si el proceso ya está abierto.
        while True:
            tasks = subprocess.check_output("tasklist", shell=True, encoding="cp850")
            if "FortniteLauncher.exe" in tasks:
                print("[*] Fortnite ya está abierto, cerrándolo...")
                os.system("taskkill /F /T /IM FortniteLauncher.exe")
            else:
                break
        access_token = await refresh_access_token(device_auth_data)
        account_id = device_auth_data["account_id"]
        launch_link = await play_fortnite(access_token, account_id)
        print("[+] Lanzando Fortnite...")
        os.system(launch_link)
    except Exception as e:
        print("[!] Error en play fortnite:", str(e))

# ---------------------------------------------------
# Nueva función: obtener display name usando el endpoint de lookup
# ---------------------------------------------------
async def get_display_name_for_account(device_auth_data: dict) -> str:
    try:
        token = await refresh_access_token(device_auth_data)
        account_id = device_auth_data["account_id"]
        url = f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{account_id}"
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return "Desconocido"
                data = await resp.json()
                return data.get("displayName", "Sin nombre")
    except Exception as ex:
        return f"Error: {ex}"

# ---------------------------------------------------
# Funciones de gestión de cuentas
# ---------------------------------------------------
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

# ---------------------------------------------------
# Callbacks para cambiar de cuenta
# ---------------------------------------------------
accounts_list = []      # Lista de tuplas (filename, data)
current_account_index = 0
event_loop = None       # Se asignará el loop en main

def on_switch_account_down():
    display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(accounts_list[current_account_index][1]), event_loop).result()
    text = f"Cuenta actual: {display_name}"
    print(f"[+] {text}")
    update_popup(text)

def on_switch_account_right():
    global current_account_index, accounts_list, event_loop
    if not accounts_list:
        print("[!] No hay cuentas guardadas.")
        return
    # Si ya estamos en la última cuenta, preguntar si se desea agregar una nueva
    if current_account_index == len(accounts_list) - 1:
        respuesta = input("¿Desea agregar una nueva cuenta? (y/n): ").strip().lower()
        if respuesta == 'y':
            new_filename = f"device_auths{len(accounts_list) + 1}.json"
            try:
                data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), event_loop).result()
                accounts_list.append((new_filename, data))
                current_account_index = len(accounts_list) - 1
                display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), event_loop).result()
                text = f"Cuenta actual: {display_name}"
                print(f"[+] Nueva cuenta agregada: {text}")
                update_popup(text)
            except Exception as ex:
                print("[!] Error al agregar nueva cuenta:", ex)
        else:
            print("[*] Permaneciendo en la cuenta actual.")
    else:
        current_account_index += 1
        display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(accounts_list[current_account_index][1]), event_loop).result()
        text = f"Cuenta actual: {display_name}"
        print(f"[+] {text}")
        update_popup(text)

def on_switch_account_left():
    global current_account_index, accounts_list
    if not accounts_list:
        print("[!] No hay cuentas guardadas.")
        return
    if current_account_index == 0:
        print("[!] Ya estás en la primera cuenta. No hay cuenta anterior.")
    else:
        current_account_index -= 1
        display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(accounts_list[current_account_index][1]), event_loop).result()
        text = f"Cuenta actual: {display_name}"
        print(f"[+] {text}")
        update_popup(text)

# ---------------------------------------------------
# Ventana Popup (Picture-in-Picture) usando tkinter
# ---------------------------------------------------
popup_root = None
popup_label = None

def create_popup():
    root = tk.Tk()
    root.overrideredirect(True)   # Sin bordes ni barra de título
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.85)
    width = 300
    height = 50
    screen_width = root.winfo_screenwidth()
    x = screen_width - width - 10
    y = 10
    root.geometry(f"{width}x{height}+{x}+{y}")
    label = tk.Label(root, text="Cuenta actual: ", font=("Arial", 12), bg="black", fg="white")
    label.pack(expand=True, fill="both")
    return root, label

def popup_loop():
    global popup_root, popup_label
    popup_root, popup_label = create_popup()
    popup_root.mainloop()

def update_popup(text: str):
    global popup_root, popup_label
    if popup_root is not None:
        # Programa la actualización en el hilo de tkinter
        popup_root.after(0, lambda: popup_label.config(text=text))

# ---------------------------------------------------
# Configuración del event loop y registro de hotkeys
# ---------------------------------------------------
def start_event_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def main():
    global accounts_list, current_account_index, event_loop, popup_root

    # Iniciar la ventana popup en el main thread
    # Para ello, ejecutamos popup_loop en un hilo separado, pero creamos primero la ventana
    popup_thread = threading.Thread(target=popup_loop, daemon=True)
    popup_thread.start()
    # Esperar hasta que el popup se haya creado
    while popup_root is None:
        time.sleep(0.1)

    # Crear el event loop en un hilo separado (daemon)
    loop = asyncio.new_event_loop()
    event_loop = loop
    loop_thread = threading.Thread(target=start_event_loop, args=(loop,), daemon=True)
    loop_thread.start()

    # Cargar cuentas existentes
    accounts_list = load_all_accounts()
    if not accounts_list:
        respuesta = input("No se encontraron cuentas guardadas. ¿Desea agregar una nueva cuenta? (y/n): ").strip().lower()
        if respuesta == 'y':
            new_filename = "device_auths1.json"
            data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), loop).result()
            accounts_list.append((new_filename, data))
            current_account_index = 0
        else:
            print("No se agregó ninguna cuenta. Saliendo...")
            return
    else:
        display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(accounts_list[current_account_index][1]), loop).result()
        print(f"[*] Se encontraron {len(accounts_list)} cuenta(s).")
        print(f"[*] Cuenta actual: {display_name}")
        update_popup(f"Cuenta actual: {display_name}")

    # Funciones que se ejecutan al presionar las hotkeys
    def on_leave_party():
        device_auth_data = accounts_list[current_account_index][1]
        asyncio.run_coroutine_threadsafe(command_leave_party(device_auth_data), loop)

    def on_skip():
        device_auth_data = accounts_list[current_account_index][1]
        asyncio.run_coroutine_threadsafe(command_skip(device_auth_data), loop)

    def on_play_fortnite():
        device_auth_data = accounts_list[current_account_index][1]
        asyncio.run_coroutine_threadsafe(command_play_fortnite(device_auth_data), loop)

    # Registrar hotkeys:
    keyboard.add_hotkey('alt gr+l', on_leave_party)
    keyboard.add_hotkey('alt gr+s', on_skip)
    keyboard.add_hotkey('alt gr+up', on_play_fortnite)
    keyboard.add_hotkey('alt gr+right', on_switch_account_right)
    keyboard.add_hotkey('alt gr+left', on_switch_account_left)
    keyboard.add_hotkey('alt gr+down', on_switch_account_down)

    # Mostrar instrucciones en consola
    print("========================================")
    print("Instrucciones y Hotkeys:")
    print("  - AltGr+L: Ejecuta 'Leave Party' con la cuenta actual")
    print("  - AltGr+S: Ejecuta 'Skip' con la cuenta actual")
    print("  - AltGr+Up: Lanza Fortnite con la cuenta actual (si ya está abierto, se cierra y relanza)")
    print("  - AltGr+Right: Cambia a la siguiente cuenta (o pregunta para agregar una nueva)")
    print("  - AltGr+Left: Cambia a la cuenta anterior")
    print("  - AltGr+Down: Muestra en consola la cuenta actual")
    print("========================================")
    print("Presione ALTGR+ESC para salir.")
    
    keyboard.wait('alt gr+esc')
    print("Saliendo...")
    loop.call_soon_threadsafe(loop.stop)
    popup_root.destroy()

if __name__ == "__main__":
    main()
