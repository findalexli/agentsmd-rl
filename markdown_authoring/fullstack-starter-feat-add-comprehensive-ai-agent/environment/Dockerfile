FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/fullstack-starter && \
    cd /workspace/fullstack-starter && \
    git remote add origin https://github.com/first-fluke/fullstack-starter.git && \
    git fetch --depth=1 origin c27ca32f487ebee7e876efabefa828ac5b4ae2e4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/fullstack-starter
