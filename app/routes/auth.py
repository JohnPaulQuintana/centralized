from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from app.services.google_auth import verify_token
from app.utils.session import create_session_cookie, COOKIE_NAME

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/verify")
async def verify_google_token(request: Request):
    data = await request.json()
    token = data.get("token")
    user_info = await verify_token(token)

    if user_info:
        cookie_value = create_session_cookie(user_info)
        response = JSONResponse({"status": "success", "user": user_info})
        response.set_cookie(
            key=COOKIE_NAME,
            value=cookie_value,
            httponly=True,
            secure=False,  # True in production (HTTPS only)
            samesite="Lax",
            max_age=60 * 60 * 24  # 1 day
        )
        return response

    return JSONResponse({"status": "error"}, status_code=401)

@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(COOKIE_NAME)
    return response