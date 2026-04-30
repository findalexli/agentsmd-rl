FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/skymp && \
    cd /workspace/skymp && \
    git remote add origin https://github.com/skyrim-multiplayer/skymp.git && \
    git fetch --depth=1 origin e899e6c4b88bada7704363a287a315168992e0d3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/skymp
