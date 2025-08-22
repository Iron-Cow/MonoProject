import calendar
from datetime import datetime

from django.utils.timezone import make_aware
from monobank.models import JarTransaction, MonoTransaction


def get_today() -> str:
    """
    Return today's date in 'YYYY-MM-DD' format.
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_daily_mono_transactions(day: str | None = None) -> list:
    """
    Return all Mono transactions for a specific day.
    Input: day as 'YYYY-MM-DD' (defaults to today)
    Output: List of dicts with amount, description, time, and category name
    """
    if day is None:
        day = get_today()

    date_obj = datetime.strptime(day, "%Y-%m-%d")
    start = make_aware(date_obj.replace(hour=0, minute=0, second=0))
    end = make_aware(date_obj.replace(hour=23, minute=59, second=59))

    transactions = MonoTransaction.objects.filter(
        time__gte=int(start.timestamp()), time__lte=int(end.timestamp())
    ).select_related("mcc__category")

    return [
        {
            "amount": tx.amount,
            "description": tx.description,
            "time": datetime.fromtimestamp(tx.time).isoformat(),
            "category": tx.mcc.category.name,
            "owner": tx.owner_name,
        }
        for tx in transactions
    ]


def get_daily_jar_transactions(day: str | None = None) -> list:
    """
    Return all Jar transactions for a specific day.
    Input: day as 'YYYY-MM-DD' (defaults to today)
    Output: List of dicts with amount, description, time, and jar name
    """
    if day is None:
        day = get_today()

    date_obj = datetime.strptime(day, "%Y-%m-%d")
    start = make_aware(date_obj.replace(hour=0, minute=0, second=0))
    end = make_aware(date_obj.replace(hour=23, minute=59, second=59))

    transactions = JarTransaction.objects.filter(
        time__gte=int(start.timestamp()), time__lte=int(end.timestamp())
    ).select_related("mcc__category")

    return [
        {
            "amount": tx.amount,
            "description": tx.description,
            "time": datetime.fromtimestamp(tx.time).isoformat(),
            "jar_name": tx.jar_name,
            "owner": tx.owner_name,
        }
        for tx in transactions
    ]


def get_monthly_mono_transactions(today: str) -> list:
    """
    Return all Mono transactions for the current month.
    Input: today as 'YYYY-MM-DD'
    Output: List of dicts with amount, description, time, and category name
    """
    date_obj = datetime.strptime(today, "%Y-%m-%d")
    start = make_aware(date_obj.replace(day=1, hour=0, minute=0, second=0))
    _, last_day = calendar.monthrange(date_obj.year, date_obj.month)
    end = make_aware(date_obj.replace(day=last_day, hour=23, minute=59, second=59))

    transactions = MonoTransaction.objects.filter(
        time__gte=int(start.timestamp()), time__lte=int(end.timestamp())
    ).select_related("mcc__category")

    return [
        {
            "amount": tx.amount,
            "description": tx.description,
            "time": datetime.fromtimestamp(tx.time).isoformat(),
            "category": tx.mcc.category.name,
            "owner": tx.owner_name,
        }
        for tx in transactions
    ]


# jar transaction
def get_monthly_jar_transactions(today: str) -> list:
    """
    Return all Jar transactions for the current month.
    Input: today as 'YYYY-MM-DD'
    Output: List of dicts with amount, description, time, and jar name
    """
    date_obj = datetime.strptime(today, "%Y-%m-%d")
    start = make_aware(date_obj.replace(day=1, hour=0, minute=0, second=0))
    _, last_day = calendar.monthrange(date_obj.year, date_obj.month)
    end = make_aware(date_obj.replace(day=last_day, hour=23, minute=59, second=59))

    transactions = JarTransaction.objects.filter(
        time__gte=int(start.timestamp()), time__lte=int(end.timestamp())
    ).select_related("mcc__category")

    return [
        {
            "amount": tx.amount,
            "description": tx.description,
            "time": datetime.fromtimestamp(tx.time).isoformat(),
            "jar_name": tx.jar_name,
            "owner": tx.owner_name,
        }
        for tx in transactions
    ]
