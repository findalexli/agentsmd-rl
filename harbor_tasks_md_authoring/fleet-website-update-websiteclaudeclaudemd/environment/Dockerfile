FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/fleet && \
    cd /workspace/fleet && \
    git remote add origin https://github.com/fleetdm/fleet.git && \
    git fetch --depth=1 origin 9ff63eb52e5016f5d9596ddad0d9ed785c58037d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/fleet
