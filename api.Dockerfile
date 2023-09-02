# syntax=docker/dockerfile:1

FROM python:3.10.6-slim-buster
WORKDIR /home

RUN pip3 install black==22.10.0
RUN pip3 install pytest
RUN pip3 install pyright==1.1.247
RUN pip3 install pytest-cov


COPY django_api/requirements.txt django_api/
RUN pip3 install -r django_api/requirements.txt

COPY django_api/api/. api/
WORKDIR /home/api

ENTRYPOINT ["python", "-m"]
