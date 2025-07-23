from collections import defaultdict
import re
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.session import get_current_user
from app.dependencies.auth import auth_required
from app.services import sheets_api  # ← import your sheets service
from app.helpers.by_keyword import find_data_by_keyword, summarize_today_vs_yesterday

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    # If using token/cookie, check and redirect
    user = get_current_user(request)
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("auth/auth.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(auth_required)):
    sheet_data = find_data_by_keyword("BAJI", "BDT")
    summary, today_label, yesterday_label = summarize_today_vs_yesterday(sheet_data)

    grouped = {
        "Daily": [],
        "Monthly": [],
        "Total": [],
    }

    for item in summary:
        metric = item["metric"].upper().strip()
        if metric.startswith("DAILY "):
            grouped["Daily"].append(item)
        elif metric.startswith("MONTHLY "):
            grouped["Monthly"].append(item)
        else:
            grouped["Total"].append(item)

    daily_order = [
        "DAILY REACH",
        "DAILY IMPRESSIONS",
        "DAILY VIEWS",
        "DAILY FOLLOWERS GAIN",
        "DAILY NEW LIKES",
        "DAILY ENGAGEMENTS",
    ]

    monthly_order = [
        "MONTHLY REACH",
        "MONTHLY IMPRESSIONS",
        "MONTHLY VIEWS",
        "MONTHLY ENGAGEMENTS",
    ]

    total_order = [
        "TOTAL REACH",
        "TOTAL IMPRESSIONS",
        "TOTAL VIEWS",
        "TOTAL FOLLOWERS",
        "TOTAL LIKES",
        "TOTAL ENGAGEMENTS",
    ]

    def sort_by_metric_order(group, order):
        order_map = {metric.upper(): i for i, metric in enumerate(order)}
        sorted_group = sorted(group, key=lambda x: order_map.get(x["metric"].upper(), len(order)))
        return sorted_group

    def group_by_category(items):
        grouped = defaultdict(list)
        for item in items:
            grouped[item["category"]].append(item)
        return list(grouped.items())  # returns List[Tuple[str, List[dict]]]

    grouped["Daily"] = group_by_category(sort_by_metric_order(grouped["Daily"], daily_order))
    grouped["Monthly"] = group_by_category(sort_by_metric_order(grouped["Monthly"], monthly_order))
    grouped["Total"] = group_by_category(sort_by_metric_order(grouped["Total"], total_order))

    # You can apply similar ordering/grouping for Monthly and Total if needed

    return templates.TemplateResponse(
        "dashboard/dashboard.html",
        {
            "request": request,
            "user": user,
            "grouped_summary": grouped,
            "today_label": today_label,
            "yesterday_label": yesterday_label,
        }
    )