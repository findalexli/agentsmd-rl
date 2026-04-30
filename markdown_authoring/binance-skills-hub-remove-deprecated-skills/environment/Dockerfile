FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/binance-skills-hub && \
    cd /workspace/binance-skills-hub && \
    git remote add origin https://github.com/binance/binance-skills-hub.git && \
    git fetch --depth=1 origin 451a781c5fa4992f54773a7dcdc396753e9fc2c0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/binance-skills-hub
