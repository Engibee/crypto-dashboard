from datetime import datetime, timedelta

def get_date_days_ago(days: int = 90) -> str:
    return (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")
