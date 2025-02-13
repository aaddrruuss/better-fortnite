import aiohttp

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
