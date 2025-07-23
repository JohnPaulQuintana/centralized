import httpx

GOOGLE_CLIENT_ID = "266581007685-pd687uda2mlgdgccdbbnsedk2lu6ssb4.apps.googleusercontent.com"

async def verify_token(token: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")

    if resp.status_code != 200:
        return None

    data = resp.json()

    # Validate the audience
    if data.get("aud") != GOOGLE_CLIENT_ID:
        return None

    # You can return more fields if needed
    return {
        "email": data.get("email"),
        "name": data.get("name"),
        "picture": data.get("picture")
    }
