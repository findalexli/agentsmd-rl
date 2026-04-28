FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/fcitx5-mcbopomofo && \
    cd /workspace/fcitx5-mcbopomofo && \
    git remote add origin https://github.com/openvanilla/fcitx5-mcbopomofo.git && \
    git fetch --depth=1 origin 025e83d834bf2746424c80ae603aaf65b3247dbf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/fcitx5-mcbopomofo
