FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/rsyslog && \
    cd /workspace/rsyslog && \
    git remote add origin https://github.com/rsyslog/rsyslog.git && \
    git fetch --depth=1 origin e0d3bd8b9312bc448d4c4253d7d30154bc8f088d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/rsyslog
