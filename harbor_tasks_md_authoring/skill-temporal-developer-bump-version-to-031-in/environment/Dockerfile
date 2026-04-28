FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/skill-temporal-developer && \
    cd /workspace/skill-temporal-developer && \
    git remote add origin https://github.com/temporalio/skill-temporal-developer.git && \
    git fetch --depth=1 origin b4fe783d421965a6368642428d17c0f52fe5f533 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/skill-temporal-developer
