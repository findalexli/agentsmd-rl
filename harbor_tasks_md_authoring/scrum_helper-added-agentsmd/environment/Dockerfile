FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/scrum-helper && \
    cd /workspace/scrum-helper && \
    git remote add origin https://github.com/fossasia/scrum_helper.git && \
    git fetch --depth=1 origin 519c4908c2caf1db2a20eb91a6fb72ea0b52b009 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/scrum-helper
