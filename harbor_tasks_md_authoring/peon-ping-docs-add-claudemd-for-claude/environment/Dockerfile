FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/peon-ping && \
    cd /workspace/peon-ping && \
    git remote add origin https://github.com/PeonPing/peon-ping.git && \
    git fetch --depth=1 origin 62fcb38d258f00bb68b3a7d91382c3822778a510 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/peon-ping
