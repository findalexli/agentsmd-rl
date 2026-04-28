FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/exchange-calendars && \
    cd /workspace/exchange-calendars && \
    git remote add origin https://github.com/gerrymanoim/exchange_calendars.git && \
    git fetch --depth=1 origin 7c67e815b9a1309e6f18c9609f3ef813d6b28eed && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/exchange-calendars
