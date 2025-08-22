import calendar
from datetime import datetime

from django.utils.timezone import make_aware
from langchain.tools import StructuredTool
from monobank.models import JarTransaction, MonoTransaction


def get_monthly_mono_transactions(today: str) -> list:
    """
    Return all Mono transactions for the current month.
    Input: today as 'YYYY-MM-DD'
    Output: List of dicts with amount, description, time, and category name

    Remember that sums written in kopiykas (cents), so you need to divide them by 100 to get the
    amount in UAH in sumary.

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


get_monthly_mono_transactions_tool = StructuredTool.from_function(
    get_monthly_mono_transactions
)


def get_monthly_jar_transactions(today: str) -> list:
    """
    Return all Jar transactions for the current month.
    Input: today as 'YYYY-MM-DD'
    Output: List of dicts with amount, description, time, owner, balance and jar name


    """
    date_obj = datetime.strptime(today, "%Y-%m-%d")
    start = make_aware(date_obj.replace(day=1, hour=0, minute=0, second=0))
    _, last_day = calendar.monthrange(date_obj.year, date_obj.month)
    end = make_aware(date_obj.replace(day=last_day, hour=23, minute=59, second=59))

    transactions = JarTransaction.objects.filter(
        time__gte=int(start.timestamp()), time__lte=int(end.timestamp())
    ).select_related("mcc__category", "account")

    return [
        {
            "amount": tx.formatted_amount,
            "description": tx.description,
            "time": tx.formatted_time,
            "jar_name": tx.jar_name,
            "owner": tx.owner_name,
            "balance": tx.formatted_balance,
        }
        for tx in transactions
    ]


get_monthly_jar_transactions_tool = StructuredTool.from_function(
    get_monthly_jar_transactions
)


def get_daily_mono_transactions(day: str | None = None) -> list:
    """
    Return all Mono transactions for a specific day.
    Input: day as 'YYYY-MM-DD' (defaults to today if None)
    Output: List of dicts with amount, description, time, and category name

    Remember that sums written in kopiykas (cents), so you need to divide them by 100 to get the
    amount in UAH in summary.
    """
    if day is None:
        day = datetime.now().strftime("%Y-%m-%d")

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


get_daily_mono_transactions_tool = StructuredTool.from_function(
    get_daily_mono_transactions
)


def get_daily_jar_transactions(day: str | None = None) -> list:
    """
    Return all Jar transactions for a specific day.
    Input: day as 'YYYY-MM-DD' (defaults to today if None)
    Output: List of dicts with amount, description, time, jar name, owner, and balance
    """
    if day is None:
        day = datetime.now().strftime("%Y-%m-%d")

    date_obj = datetime.strptime(day, "%Y-%m-%d")
    start = make_aware(date_obj.replace(hour=0, minute=0, second=0))
    end = make_aware(date_obj.replace(hour=23, minute=59, second=59))

    transactions = JarTransaction.objects.filter(
        time__gte=int(start.timestamp()), time__lte=int(end.timestamp())
    ).select_related("mcc__category", "account")

    return [
        {
            "amount": tx.formatted_amount,
            "description": tx.description,
            "time": tx.formatted_time,
            "jar_name": tx.jar_name,
            "owner": tx.owner_name,
            "balance": tx.formatted_balance,
        }
        for tx in transactions
    ]


get_daily_jar_transactions_tool = StructuredTool.from_function(
    get_daily_jar_transactions
)
