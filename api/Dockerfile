FROM python:3.10.6-slim-buster
WORKDIR /api
ARG APP_DIR

COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY src ./
RUN useradd nonroot && chown nonroot: /api

USER nonroot
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

