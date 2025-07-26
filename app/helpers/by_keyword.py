# from datetime import datetime, timedelta
# import calendar
# from app.services import sheets_api
# from collections import OrderedDict

# sheet_url = f"https://docs.google.com/spreadsheets/d/{sheets_api.SPREADSHEET_ID}"

# def get_column_letters(n):
#     letters = []
#     for i in range(n):
#         result = ''
#         col = i
#         while col >= 0:
#             result = chr(col % 26 + ord('A')) + result
#             col = col // 26 - 1
#         letters.append(result)
#     return letters

# def find_data_by_keyword(sheet_name: str, keyword: str, column="A", num_rows=17, max_columns=200):
#     full_range = f"{sheet_name}!{column}1:{column}"
#     data = sheets_api.read_sheet(full_range)
#     start_row = None

#     for i, row in enumerate(data):
#         if row and row[0].strip() == keyword:
#             start_row = i - 1
#             break

#     if start_row is None or start_row < 0:
#         raise ValueError(f"Keyword '{keyword}' not found or no row above it.")

#     end_row = start_row + num_rows
#     col_letters = get_column_letters(max_columns)
#     col_range = f"{col_letters[0]}{start_row+1}:{col_letters[-1]}{end_row}"
#     range_ = f"{sheet_name}!{col_range}"
#     return sheets_api.read_sheet(range_)

# def parse_number(value: str):
#     try:
#         return int(str(value).replace(",", "").strip())
#     except (ValueError, TypeError):
#         return 0

# def parse_date_flexibly(date_str):
#     for fmt in ("%d/%m/%Y", "%d/%m/%y", "%-d/%-m/%y", "%-d/%-m/%Y", "%d/%m"):
#         try:
#             return datetime.strptime(date_str.strip(), fmt)
#         except:
#             continue
#     return None

# def summarize_metrics_with_chart_data(sheet_data, month: str = None):
#     metric_category_map = {
#         "TOTAL FOLLOWERS": "Followers",
#         "DAILY FOLLOWERS GAIN": "Followers",
#         "DAILY ENGAGEMENTS": "Engagements",
#         "MONTHLY ENGAGEMENTS": "Engagements",
#         "TOTAL ENGAGEMENTS": "Engagements",
#         "TOTAL LIKES": "Engagements",
#         "DAILY NEW LIKES": "Engagements",
#         "DAILY IMPRESSIONS": "Impressions",
#         "MONTHLY IMPRESSIONS": "Impressions",
#         "TOTAL IMPRESSIONS": "Impressions",
#         "DAILY REACH": "Reach",
#         "MONTHLY REACH": "Reach",
#         "TOTAL REACH": "Reach",
#         "DAILY VIEWS": "Views",
#         "MONTHLY VIEWS": "Views",
#         "TOTAL VIEWS": "Views"
#     }

#     if not sheet_data or len(sheet_data) < 2:
#         return [], "", "", []

#     date_row = sheet_data[0]
#     raw_dates = date_row[3:]
#     parsed_dates = [parse_date_flexibly(str(d)) for d in raw_dates]
#     date_to_index = {d.strftime("%d/%m"): i for i, d in enumerate(parsed_dates) if d}

#     now = datetime.now()
#     current_day = now.day - 1 #to get today=yesterday
#     current_month = now.month
#     current_year = now.year

#     # Build full chart label list
#     if month:
#         month_number = list(calendar.month_name).index(month.title())
#         is_current_month = (month_number == current_month)
#         limit_day = current_day if is_current_month else calendar.monthrange(current_year, month_number)[1]

#         full_dates = [
#             datetime(current_year, month_number, d)
#             for d in range(1, limit_day + 1)
#         ]
#     else:
#         full_dates = [d for d in parsed_dates if d]

#     full_labels = [d.strftime("%d/%m") for d in full_dates]
#     full_labels_string = [d.strftime("%b %d") for d in full_dates]

#     parsed = []

#     for row in sheet_data[1:]:
#         if len(row) > 3:
#             metric = str(row[1]).strip().upper()
#             values_all = [parse_number(v) for v in row[3:]]

#             aligned_values = []
#             for label in full_labels:
#                 idx = date_to_index.get(label)
#                 value = values_all[idx] if idx is not None and idx < len(values_all) else 0
#                 aligned_values.append(value)

#             # Reverse for chart and metrics
#             aligned_values = aligned_values[::-1]
#             reversed_labels = full_labels[::-1]

#             today = aligned_values[0] if aligned_values else 0
#             yesterday = aligned_values[1] if len(aligned_values) >= 2 else 0
#             delta = today - yesterday

#             parsed.append({
#                 "sheet_url": sheet_url,
#                 "metric": metric,
#                 "category": metric_category_map.get(metric, "Other"),
#                 "today": today,
#                 "yesterday": yesterday,
#                 "delta": delta,
#                 "change": (
#                     "increase" if delta > 0 else
#                     "decrease" if delta < 0 else
#                     "stable"
#                 ),
#                 "chart": {
#                     "labels": full_labels_string[::-1],
#                     "values": aligned_values
#                 }
#             })

#     return parsed, reversed_labels[0] if reversed_labels else "", reversed_labels[1] if len(reversed_labels) > 1 else "", reversed_labels


# Optimized Version:
from datetime import datetime
import calendar
from app.services import sheets_api
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

sheet_urls = sheets_api.ID_LISTS

def get_column_letters(n):
    letters = []
    for i in range(n):
        result = ''
        col = i
        while col >= 0:
            result = chr(col % 26 + ord('A')) + result
            col = col // 26 - 1
        letters.append(result)
    return letters

def find_data_by_keyword(sheet_name: str, keyword: str, type: str, num_rows: int, column="A", max_columns=200):
    # Read once from A1 to Z100 or enough for safety
    full_range = f"{sheet_name}!A1:{get_column_letters(max_columns)[-1]}100"
    data = sheets_api.read_sheet(full_range, type)

    start_row = None
    for i, row in enumerate(data):
        if row and row[0].strip() == keyword:
            start_row = i - 1
            break

    if start_row is None or start_row < 0:
        raise ValueError(f"Keyword '{keyword}' not found or no row above it.")

    return data[start_row:start_row + num_rows]

def parse_number(value: str):
    try:
        return int(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0

def parse_date_flexibly(date_str):
    if not date_str or not str(date_str).strip():
        return None
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%-d/%-m/%y", "%-d/%-m/%Y", "%d/%m"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def summarize_metrics_with_chart_data(sheet_data, month: str = None, platform: str = 'fb'):

    if platform == "fb":
        metric_category_map = {
            "TOTAL FOLLOWERS": "Followers",
            "DAILY FOLLOWERS GAIN": "Followers",
            "DAILY ENGAGEMENTS": "Engagements",
            "MONTHLY ENGAGEMENTS": "Engagements",
            "TOTAL ENGAGEMENTS": "Engagements",
            "TOTAL LIKES": "Engagements",
            "DAILY NEW LIKES": "Engagements",
            "DAILY IMPRESSIONS": "Impressions",
            "MONTHLY IMPRESSIONS": "Impressions",
            "TOTAL IMPRESSIONS": "Impressions",
            "DAILY REACH": "Reach",
            "MONTHLY REACH": "Reach",
            "TOTAL REACH": "Reach",
            "DAILY VIEWS": "Views",
            "MONTHLY VIEWS": "Views",
            "TOTAL VIEWS": "Views"
        }

    elif platform in ["ig","yt"]:
        metric_category_map = {
            "TOTAL FOLLOWERS": "Followers",
            "DAILY FOLLOWERS GAIN": "Followers",
            "DAILY ENGAGEMENTS": "Engagements",
            "MONTHLY ENGAGEMENTS": "Engagements",
            "TOTAL ENGAGEMENTS": "Engagements",
            "DAILY IMPRESSIONS": "Impressions",
            "MONTHLY IMPRESSIONS": "Impressions",
            "TOTAL IMPRESSIONS": "Impressions",
            "DAILY REACH": "Reach",
            "MONTHLY REACH": "Reach",
            "TOTAL REACH": "Reach",
        }

    elif platform == "x":
        metric_category_map = {
            "TOTAL FOLLOWERS": "Followers",
            "DAILY FOLLOWERS GAIN": "Followers",
            "DAILY ENGAGEMENTS": "Engagements",
            "MONTHLY ENGAGEMENTS": "Engagements",
            "TOTAL ENGAGEMENTS": "Engagements",
            "DAILY VIEWS": "Views",
            "MONTHLY VIEWS": "Views",
            "TOTAL VIEWS": "Views",
        }
    if not sheet_data or len(sheet_data) < 2:
        return [], "", "", []

    date_row = sheet_data[0]
    raw_dates = date_row[3:]
    parsed_dates = [parse_date_flexibly(str(d)) for d in raw_dates]
    date_to_index = {d.strftime("%d/%m"): i for i, d in enumerate(parsed_dates) if d}

    now = datetime.now()
    current_day = now.day - 1
    current_month = now.month
    current_year = now.year

    if month:
        month_number = list(calendar.month_name).index(month.title())
        is_current_month = (month_number == current_month)
        limit_day = current_day if is_current_month else calendar.monthrange(current_year, month_number)[1]

        full_dates = [datetime(current_year, month_number, d) for d in range(1, limit_day + 1)]
    else:
        full_dates = [d for d in parsed_dates if d]

    full_labels = [d.strftime("%d/%m") for d in full_dates]
    full_labels_string = [d.strftime("%b %d") for d in full_dates]

    def process_row(row, platform):
        if len(row) <= 3:
            return None
        metric = str(row[1]).strip().upper()
        values_all = [parse_number(v) for v in row[3:]]

        aligned_values = []
        for label in full_labels:
            idx = date_to_index.get(label)
            value = values_all[idx] if idx is not None and idx < len(values_all) else 0
            aligned_values.append(value)

        aligned_values = aligned_values[::-1]
        today = aligned_values[0] if aligned_values else 0
        yesterday = aligned_values[1] if len(aligned_values) >= 2 else 0
        delta = today - yesterday
        url = ''
        if platform == "fb":
            url = f"https://docs.google.com/spreadsheets/d/{sheet_urls[0]}"
        elif platform == "ig":
            url = f"https://docs.google.com/spreadsheets/d/{sheet_urls[1]}"
        elif platform == "yt":
            url = f"https://docs.google.com/spreadsheets/d/{sheet_urls[2]}"
        elif platform == "x":
            url = f"https://docs.google.com/spreadsheets/d/{sheet_urls[3]}"

        return {
            "sheet_url": url,
            "metric": metric,
            "category": metric_category_map.get(metric, "Other"),
            "today": today,
            "yesterday": yesterday,
            "delta": delta,
            "change": "increase" if delta > 0 else "decrease" if delta < 0 else "stable",
            "chart": {
                "labels": full_labels_string[::-1],
                "values": aligned_values
            }
        }

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_row, sheet_data[1:], repeat(platform)))

    parsed = [r for r in results if r]
    reversed_labels = full_labels[::-1]
    return parsed, reversed_labels[0] if reversed_labels else "", reversed_labels[1] if len(reversed_labels) > 1 else "", reversed_labels
