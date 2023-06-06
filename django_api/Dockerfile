FROM python:3.10.6-slim-buster
WORKDIR /api
ARG APP_DIR

COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install redis
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY api ./
RUN useradd nonroot && chown nonroot: /api


USER nonroot
CMD ["python", "manage.py", "makemigrations"]
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "loaddata", "categories.json"]
CMD ["python", "manage.py", "loaddata", "categories_mso.json"]
CMD ["python", "manage.py", "loaddata", "currency.json"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]