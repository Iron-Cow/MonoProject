FROM python:3.10.6-slim-bullseye
WORKDIR /chatbot
ARG APP_DIR

COPY ./requirements.txt ./
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl-dev \
    tk-dev && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY src .


CMD ["python", "-m", "bot"]
