# syntax=docker/dockerfile:1

FROM python:3.10.6-slim-bullseye
WORKDIR /home

RUN pip3 install black==25.1.0
RUN pip3 install pytest==7.4.2
RUN pip3 install pyright==1.1.403
RUN pip3 install pytest-cov


COPY django_api/requirements.txt django_api/
RUN pip3 install -r django_api/requirements.txt

COPY django_api/api/. api/
COPY pyproject.toml api/

WORKDIR /home/api

ENTRYPOINT ["python", "-m"]
