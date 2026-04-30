FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/win-codexbar && \
    cd /workspace/win-codexbar && \
    git remote add origin https://github.com/Finesssee/Win-CodexBar.git && \
    git fetch --depth=1 origin 4f155aa0d96327e65edc1c3107364cead1b3ded2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/win-codexbar
