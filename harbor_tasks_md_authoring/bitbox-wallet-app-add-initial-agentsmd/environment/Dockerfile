FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bitbox-wallet-app && \
    cd /workspace/bitbox-wallet-app && \
    git remote add origin https://github.com/BitBoxSwiss/bitbox-wallet-app.git && \
    git fetch --depth=1 origin d78450d9149ecac035c239df1045af1381d589f0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bitbox-wallet-app
