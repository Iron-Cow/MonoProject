FROM python:3.10.6-slim-buster
WORKDIR /chatbot
ARG APP_DIR

COPY ./requirements.txt ./

RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY src .


CMD ["python", "-m", "bot"]

