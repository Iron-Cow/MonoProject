FROM python:3.10-slim
WORKDIR /api
ARG APP_DIR
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY api ./
COPY ./entrypoint.sh ./
RUN chmod 777 ./entrypoint.sh
RUN useradd nonroot && chown nonroot: /api

USER nonroot

# Specify the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EXPOSE 5432
