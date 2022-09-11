import logging

from fastapi import FastAPI, Request, Response
import uvicorn

from starlette.responses import JSONResponse


from data_management.config import config
from sqlalchemy.dialects.postgresql import insert

from serializers.serializer import UserSerializer

logger = logging.Logger("api")
app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):

    secret_key_from_headers = request.headers.get("chat_bot_api_key")
    print(config.CHAT_BOT_API_KEY)
    if config.CHAT_BOT_API_KEY != secret_key_from_headers:
        error_text = "Invalid CHAT_BOT_API_KEY header"
        logger.error(error_text)
        return JSONResponse({"error": error_text}, status_code=400)

    response = await call_next(request)
    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/users/{tg_id}")
def create_user(tg_id: str, q: str | None = None):
    data = UserSerializer({"tg_id": tg_id})

    # query = query = insert(table).values(values).on_conflict_do_nothing()
    return data.data


if __name__ == '__main__':
    print("Starting local run")
    uvicorn.run(app, host="0.0.0.0", port=8000)
