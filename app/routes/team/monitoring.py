from collections import defaultdict
import re
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.session import get_current_user
from app.dependencies.auth import auth_required
from app.services import sheets_api  # ← import your sheets service
from app.helpers.by_keyword import find_data_by_keyword, summarize_metrics_with_chart_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/monitoring", response_class=HTMLResponse)
def index(request: Request):
    # If using token/cookie, check and redirect
    user = get_current_user(request)
    if user:
        print("User is authenticated, redirecting to dashboard")
        print(user)
        # return RedirectResponse("/monitoring/dashboard")
    return templates.TemplateResponse("team/dashboard.html", {"request": request, "user": user,})