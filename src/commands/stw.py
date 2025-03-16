import aiohttp
import time
import keyboard
import pydirectinput
import asyncio

pydirectinput.PAUSE = 0

# Coordenadas para la acción "fast drop"
xMax, yMax = 1194, 600
xDrop, yDrop = 799, 672

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
        rewards_guids = [
            guid 
            for guid, details in items.items() 
            if details.get("templateId", "").startswith("CardPack:")
        ]
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
                raise Exception(
                    f"Error al reclamar la recompensa de la misión: {resp.status} {text_error}"
                )
    return True


# ==================================================
# FUNCIÓN ASÍNCRONA DE FAST DROP
# (Para ser llamada repetidamente mientras se mantenga la tecla)
# ==================================================
def fast_drop():
    """
    Realiza las acciones de 'fast drop':
    1) Presiona la tecla 'X'
    2) Clic en 'Max' (coordenadas xMax, yMax)
    3) Clic en 'Drop' (coordenadas xDrop, yDrop)
    """
    # Presionar la tecla X
    pydirectinput.press('x')
    time.sleep(0.015)

    # Moverse al botón Max y simular un clic
    pydirectinput.moveTo(xMax, yMax, duration=0)
    pydirectinput.click()
    pydirectinput.mouseDown()
    time.sleep(0.015)
    pydirectinput.mouseUp()

    time.sleep(0.015)

    # Moverse al botón Drop y hacer clic
    pydirectinput.moveTo(xDrop, yDrop, duration=0)
    pydirectinput.click()