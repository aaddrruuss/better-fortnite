import asyncio
import os
import subprocess
from auth.auth import new_token
from commands.party import getPartyId, leaveParty
from commands.stw import OpenCardPackBatch, claimMissionAlertRewards, claimQuestRewards
from commands.launch import play_fortnite
from ui.cmd_interface import cmd_interface

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
        cmd_interface()
    except Exception as e:
        print("[!] Error en leave party:", str(e))
        cmd_interface()

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
        cmd_interface()
    except Exception as e:
        print("[!] Error en skip:", str(e))
        cmd_interface()

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
        cmd_interface()
    except Exception as e:
        print("[!] Error en play fortnite:", str(e))
        cmd_interface()
