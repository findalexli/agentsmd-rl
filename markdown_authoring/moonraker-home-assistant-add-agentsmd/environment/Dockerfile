FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/moonraker-home-assistant && \
    cd /workspace/moonraker-home-assistant && \
    git remote add origin https://github.com/marcolivierarsenault/moonraker-home-assistant.git && \
    git fetch --depth=1 origin 0e42c2b9abb8f1821453ede180987ce327dbf8e6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/moonraker-home-assistant
