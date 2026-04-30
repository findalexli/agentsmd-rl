FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/eclipse.platform.ui && \
    cd /workspace/eclipse.platform.ui && \
    git remote add origin https://github.com/eclipse-platform/eclipse.platform.ui.git && \
    git fetch --depth=1 origin 40763b618509bbbd1d6e5a8cb3945ce686b68da0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/eclipse.platform.ui
