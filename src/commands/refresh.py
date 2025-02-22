import asyncio
import os
import subprocess


from colorama import Fore, init
init()

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
        print(Fore.LIGHTYELLOW_EX + "[*] Executing command: Leave Party" + Fore.RESET)
        access_token = await refresh_access_token(device_auth_data)
        account_id = device_auth_data["account_id"]
        party_id = await getPartyId(access_token, account_id)
        await leaveParty(access_token, party_id, account_id)
        os.system("cls")
        print(Fore.LIGHTGREEN_EX + "[+] You have left your party successfully." + Fore.RESET)
        cmd_interface()
    except Exception as e:
        os.system("cls")
        print(Fore.LIGHTRED_EX + "[!] Error leaving party:" + Fore.RESET, str(e))
        cmd_interface()

async def command_skip(device_auth_data: dict):
    try:
        print(Fore.LIGHTYELLOW_EX + "[*] Executing command: Skip" + Fore.RESET)
        access_token = await refresh_access_token(device_auth_data)
        account_id = device_auth_data["account_id"]
        party_id = await getPartyId(access_token, account_id)
        await leaveParty(access_token, party_id, account_id)
        await OpenCardPackBatch(access_token, account_id)
        await claimMissionAlertRewards(access_token, account_id)
        for _ in range(6):
            await claimQuestRewards(access_token, account_id)
        os.system("cls")
        print(Fore.LIGHTGREEN_EX + "[+] Skip command executed successfully" + Fore.RESET)
        cmd_interface()
    except Exception as e:
        os.system("cls")
        print(Fore.LIGHTRED_EX + "[!] Error skipping mission:" + Fore.RESET, str(e))
        cmd_interface()

async def command_play_fortnite(device_auth_data: dict):
    try:
        print(Fore.LIGHTYELLOW_EX + "[*] Executing command: Play Fortnite" + Fore.RESET)
        # Se verifica en un bucle si el proceso ya está abierto.
        while True:
            tasks = subprocess.check_output("tasklist", shell=True, encoding="cp850")
            if "FortniteLauncher.exe" in tasks:
                print(Fore.LIGHTYELLOW_EX + "[*] Fortnite ya está abierto, cerrándolo..." + Fore.RESET)
                os.system("taskkill /F /T /IM FortniteLauncher.exe")
            else:
                break
        access_token = await refresh_access_token(device_auth_data)
        account_id = device_auth_data["account_id"]
        launch_link = await play_fortnite(access_token, account_id)
        os.system("cls")
        print(Fore.LIGHTGREEN_EX + "[+] Launching Fortnite..." + Fore.RESET)
        os.system(launch_link)
        cmd_interface()
    except Exception as e:
        os.system("cls")
        print(Fore.LIGHTGREEN_EX + "[!] Error on play fortnite:" + Fore.RESET, str(e))
        cmd_interface()
