import httpx

GOOGLE_CLIENT_ID = "266581007685-pd687uda2mlgdgccdbbnsedk2lu6ssb4.apps.googleusercontent.com"

ALLOWED_EMAILS = {"jpquintana2024@gmail.com", "flynn.rider@auroramy.com", "jpquintana01@gmail.com", "exousia.navi@auroramy.com"}

async def verify_token(token: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")

    if resp.status_code != 200:
        return None

    data = resp.json()

    if data.get("aud") != GOOGLE_CLIENT_ID:
        return None

    email = data.get("email")

    if email not in ALLOWED_EMAILS:
        return None  # Unauthorized email

    return {
        "email": email,
        "name": data.get("name"),
        "picture": data.get("picture")
    }

