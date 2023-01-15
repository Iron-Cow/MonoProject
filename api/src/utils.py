import time

from errors import MONO_TOO_MANY_REQUESTS_ERROR
from log_util import Logger, configure_logging



from requests import get

from sqlalchemy.exc import IntegrityError

from serializers.serializer import ClientInfoWithAccountsSerializer, ClientInfoSerializer, TransactionSerializer
from data_management.tables import Monobank_Account, db_manager, Monobank_Card, Monobank_Jar, Monobank_Transaction
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update
from sqlalchemy.sql import select

from worker import create_task

logger = Logger("utils")
configure_logging()

MONO_API_URL = "https://api.monobank.ua"
PERSONAL_INFO_PATH = "/personal/client-info"
TRANSACTIONS_PATH = "/personal/statement"

ACCEPTABLE_ACCOUNT_TYPES = ["card", "jar"]


def get_monouser_accounts_summary(monotoken: str):
    url = MONO_API_URL + PERSONAL_INFO_PATH
    headers = {
        "X-Token": monotoken
    }
    user_data = get(url, headers=headers)
    return user_data.json()


def get_monouser_transaction_info(monotoken: str, account: str, from_timestamp: int = None, to_timestamp: int = None):
    if not from_timestamp:
        from_timestamp = int(time.time()) - 2678400  # 31 * 24 * 60 * 60
    url = f"{MONO_API_URL}{TRANSACTIONS_PATH}/{account}/{from_timestamp}"

    if to_timestamp:
        url = f"{url}/{to_timestamp}"

    headers = {
        "X-Token": monotoken
    }
    user_data = get(url, headers=headers)
    if user_data.status_code == 429:
        raise MONO_TOO_MANY_REQUESTS_ERROR
    return user_data.json()


def update_account_values(user_data: dict,
                          update_transactions: bool = False,
                          monotoken_given: str = None,
                          single_account_to_update: str = None):
    # create/update user account
    client_info_data = ClientInfoSerializer(user_data).data
    table = Monobank_Account
    query = insert(table).values(client_info_data).on_conflict_do_nothing()
    result = db_manager.execute_dml_query(query)
    full_data = ClientInfoWithAccountsSerializer(user_data).data
    accounts = full_data.get("accounts")
    monotoken = full_data.get("monotoken") or monotoken_given
    tg_id = full_data.get("tg_id")
    if accounts:
        # create/update cards
        for account in accounts:
            account_id = account.get("account_id", "")
            if single_account_to_update and single_account_to_update != account_id:
                continue
            logger.info("updating monocard", f"updating card {account_id} for {full_data.get('name')}")
            print(account)
            table = Monobank_Card
            query = insert(table).values(account)
            try:
                db_manager.execute_dml_query(query)
            except IntegrityError as err:
                query = update(table) \
                    .where(table.c.account_id == account_id) \
                    .values(**{k: v for k, v in account.items()}
                            )
                db_manager.execute_dml_query(query)
                print("error", err)
                pass
            if update_transactions:
                try:
                    upsert_transactions_by_account_id(monotoken, account_id, "card")
                    logger.error("Successfully updated account", account_id)
                except MONO_TOO_MANY_REQUESTS_ERROR:
                    create_task.delay(tg_id, account_id, "card")
                    logger.error("MONO_TOO_MANY_REQUESTS_ERROR", "")

    jars = full_data.get("jars")
    if jars:
        # create/update jars
        for jar in jars:
            jar_id = jar.get("jar_id")
            if single_account_to_update and single_account_to_update != jar_id:
                continue
            logger.info("updating monojar", f"updating jar {jar_id} for {full_data.get('name')}")
            print(jar)
            table = Monobank_Jar
            query = insert(table).values(jar).on_conflict_do_nothing()
            result = db_manager.execute_dml_query(query)
            print(result)
            if update_transactions:
                try:
                    upsert_transactions_by_account_id(monotoken, jar_id, "jar")
                    logger.error("Successfully updated jar", jar_id)
                except MONO_TOO_MANY_REQUESTS_ERROR:
                    create_task.delay(tg_id, jar_id, "jar")
                    logger.error("MONO_TOO_MANY_REQUESTS_ERROR", "")


def get_monotoken_by_tg_id(tg_id: str) -> str:
    query = select(Monobank_Account).where(Monobank_Account.c.tg_id == tg_id)
    result = db_manager.execute_select_query(
        query
    )
    if not result:
        raise Exception("Not found")
    return result[0].get("monotoken")

def upsert_transactions_by_account_id(monotoken: str, account_id: str, account_type: str):
    transactions = get_monouser_transaction_info(monotoken, account_id)
    _upsert_transactions(transactions, account_id, account_type)

def _upsert_transactions(transactions: list[dict], account_id: str, account_type: str):
    if account_type not in ACCEPTABLE_ACCOUNT_TYPES:
        logger.error("Unacceptable account type to update", account_type)
        return
    serializer = TransactionSerializer(transactions, many=True)
    data = serializer.data
    for transaction in data:
        table = Monobank_Transaction
        query = insert(table).values(
            transaction | {"account_type": account_type, "account_id": account_id}
        ).on_conflict_do_nothing()
        db_manager.execute_dml_query(query)
