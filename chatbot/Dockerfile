FROM python:3.10.6-slim-buster
WORKDIR /api
ARG APP_DIR

COPY ./requirements.txt ./

RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY src src

RUN useradd nonroot && chown nonroot: /api

USER nonroot
CMD ["python", "-m", "src.bot"]

