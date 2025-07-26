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

daily_order = [
        "DAILY FOLLOWERS GAIN", "DAILY IMPRESSIONS","DAILY REACH","DAILY VIEWS",
        "DAILY NEW LIKES", "DAILY ENGAGEMENTS"
    ]
monthly_order = [
        "MONTHLY IMPRESSIONS","MONTHLY REACH", "MONTHLY VIEWS", "MONTHLY ENGAGEMENTS"
    ]
total_order = [
        "TOTAL FOLLOWERS", "TOTAL IMPRESSIONS", "TOTAL REACH","TOTAL VIEWS",
        "TOTAL LIKES", "TOTAL ENGAGEMENTS"
    ]

def sort_by_metric_order(group, order):
        order_map = {metric.upper(): i for i, metric in enumerate(order)}
        return sorted(group, key=lambda x: order_map.get(x["metric"].upper(), len(order)))

def group_by_category(items):
        grouped = defaultdict(list)
        for item in items:
            grouped[item["category"]].append(item)
        return list(grouped.items())

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    # If using token/cookie, check and redirect
    user = get_current_user(request)
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("auth/auth.html", {"request": request})

@router.get("/api/dashboard-data")
def get_dashboard_data(brand: str, currency: str, month: str, platform:str):
    num_rows = 17
    if platform == "fb":
         num_rows = 17
    elif platform in ["ig", "yt"]:
         num_rows = 12
    elif platform == "x":
         num_rows = 9
    sheet_data = find_data_by_keyword(brand, currency, platform, num_rows)
    # summary, today_label, yesterday_label, labels = summarize_metrics_with_chart_data(sheet_data)
    # 2. Parse with optional month filter
    summary, today_label, yesterday_label, labels = summarize_metrics_with_chart_data(sheet_data, month, platform)
    print("SUMMARY:")
    print(summary)
    grouped = {
        "Daily": group_by_category(sort_by_metric_order(
            [i for i in summary if i["metric"].startswith("DAILY")], daily_order)),
        "Monthly": group_by_category(sort_by_metric_order(
            [i for i in summary if i["metric"].startswith("MONTHLY")], monthly_order)),
        "Total": group_by_category(sort_by_metric_order(
            [i for i in summary if i["metric"].startswith("TOTAL")], total_order)),
    }

    return {
        "grouped_summary": grouped,
        "today_label": today_label,
        "yesterday_label": yesterday_label,
        "date_labels": labels
    }

yesterday = datetime.now() - timedelta(days=1)
yesterday_label = yesterday.strftime('%d/%m/%Y')
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(auth_required)):
    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "user": user,
            "today_label": yesterday_label,
        }
    )