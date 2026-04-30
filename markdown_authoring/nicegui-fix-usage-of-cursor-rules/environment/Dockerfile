FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nicegui && \
    cd /workspace/nicegui && \
    git remote add origin https://github.com/zauberzeug/nicegui.git && \
    git fetch --depth=1 origin 4ecfe7868992de68a7be65b1c8c77ca4861929fd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nicegui
