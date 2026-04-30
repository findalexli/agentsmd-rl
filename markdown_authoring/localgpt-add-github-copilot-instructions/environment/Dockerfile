FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/localgpt && \
    cd /workspace/localgpt && \
    git remote add origin https://github.com/localgpt-app/localgpt.git && \
    git fetch --depth=1 origin 2b28f6d0bfa1927bbee33efa15f588f1d21100e2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/localgpt
