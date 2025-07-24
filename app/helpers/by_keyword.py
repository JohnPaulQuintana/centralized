from app.services import sheets_api

def find_data_by_keyword(sheet_name: str, keyword: str, column="A", num_rows=17, num_columns=10):
    full_range = f"{sheet_name}!{column}1:{column}"
    data = sheets_api.read_sheet(full_range)

    start_row = None
    for i, row in enumerate(data):
        if row and row[0].strip() == keyword:
            start_row = i - 1
            break

    if start_row is None or start_row < 0:
        raise ValueError(f"Keyword '{keyword}' not found or no row above it.")

    end_row = start_row + num_rows
    col_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"][:num_columns]
    range_ = f"{sheet_name}!{col_letters[0]}{start_row+1}:{col_letters[-1]}{end_row}"
    return sheets_api.read_sheet(range_)

def parse_number(value: str):
    try:
        return int(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0

def summarize_metrics_with_chart_data(sheet_data):
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

    if not sheet_data or len(sheet_data) < 2:
        return [], "", "", []

    date_row = sheet_data[0]
    date_labels = [str(d).strip() for d in date_row[3:10]]

    parsed = []
    for row in sheet_data[1:]:
        if len(row) >= 10:
            metric = str(row[1]).strip().upper()
            today = parse_number(row[3])
            yesterday = parse_number(row[4])
            delta = today - yesterday
            values = [parse_number(v) for v in row[3:10]]

            parsed.append({
                "metric": metric,
                "category": metric_category_map.get(metric, "Other"),
                "today": today,
                "yesterday": yesterday,
                "delta": delta,
                "change": (
                    "increase" if delta > 0 else
                    "decrease" if delta < 0 else
                    "no change"
                ),
                "chart": {
                    "labels": date_labels,
                    "values": values
                }
            })
    assert isinstance(date_labels, list), f"date_labels is not a list: {type(date_labels)}"

    return parsed, date_labels[0] if len(date_labels) > 0 else "", date_labels[1] if len(date_labels) > 1 else "", date_labels
