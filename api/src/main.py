from errors import MONO_TOO_MANY_REQUESTS_ERROR
from log_util import Logger, configure_logging
from fastapi import FastAPI, Request, Response
import uvicorn

from starlette.responses import JSONResponse

from serializers.serializer import ClientInfoSerializer, ClientInfoWithAccountsSerializer
from data_management.config import config
from sqlalchemy.dialects.postgresql import insert

from data_management.tables import Monobank_Account, db_manager
from serializers.serializer import UserSerializer
from utils import (
    get_monouser_accounts_summary,
    update_account_values,
    get_monotoken_by_tg_id,
    upsert_transactions_by_account_id,
)
from tests.mocks import CLIENT_INFO_MOCK

from worker import create_task

logger = Logger("api")
configure_logging()
app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    secret_key_from_headers = request.headers.get("chat_bot_api_key")
    if config.CHAT_BOT_API_KEY != secret_key_from_headers:
        error_text = "Invalid CHAT_BOT_API_KEY header"
        logger.error(error_text)
        return JSONResponse({"error": error_text}, status_code=400)

    response = await call_next(request)
    return response


@app.get("/")
def read_root():
    token = "sometoken"
    user_data = get_monouser_accounts_summary(monotoken=token) | {"monotoken": token}
    # user_data = CLIENT_INFO_MOCK | {"monotoken": token}
    # print(user_data)
    # serializer = ClientInfoSerializer(user_data)

    serializer = ClientInfoWithAccountsSerializer(user_data)
    # print(serializer.data)
    # table = Monobank_Account
    # query = insert(table).values(serializer.data).on_conflict_do_nothing()
    # db_manager.execute_dml_query(query)
    update_account_values(user_data, update_transactions=True)
    return {"data": user_data, "result_data": serializer.data}


@app.post("/users/{tg_id}")
async def create_user(tg_id: str, request: Request):
    body = await request.json()
    token = body.get("monotoken")
    if not token:
        return "something bad"
    user_data = get_monouser_accounts_summary(monotoken=token) | {"monotoken": token, "tg_id": tg_id}
    serializer = ClientInfoWithAccountsSerializer(user_data)
    update_account_values(user_data, update_transactions=True)
    # create_task.delay(5)
    data = await request.json()
    # query = query = insert(table).values(values).on_conflict_do_nothing()
    return "ok"


@app.post("/users/{tg_id}/update_account")
async def update_mono_account(tg_id: str, request: Request):
    body = await request.json()
    account_id, account_type, debug_sleep_time = body.get("account_id", ""), body.get("account_type", ""), body.get(
        "debug_sleep_time", 120),

    logger.info(key="Updating account", story=f"{account_type} {account_id}")
    monotoken = get_monotoken_by_tg_id(tg_id)
    upsert_transactions_by_account_id(monotoken, account_id, account_type)
    try:
        upsert_transactions_by_account_id(monotoken, account_id, account_type)
        logger.error(f"Successfully updated {account_type}", account_id)
    except MONO_TOO_MANY_REQUESTS_ERROR:
        create_task.delay(tg_id, account_id, account_type, debug_sleep_time)
        logger.error("MONO_TOO_MANY_REQUESTS_ERROR", f"Created celery task to retrigger {account_id}")
    return "ok"


if __name__ == '__main__':
    print("Starting local run")
    uvicorn.run(app, host="0.0.0.0", port=8000)
