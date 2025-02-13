import os
import time
import base64
import asyncio
import aiohttp
from config import EPIC_CLIENT_ID_SWITCH, EPIC_CLIENT_SECRET_SWITCH, OAUTH_TOKEN_URL, DEVICE_CODE_URL

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
