FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/wynntils && \
    cd /workspace/wynntils && \
    git remote add origin https://github.com/Wynntils/Wynntils.git && \
    git fetch --depth=1 origin a675c1a4d9b5312af9526107b0695b903f4b7fa4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/wynntils
