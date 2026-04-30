FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/xmlui && \
    cd /workspace/xmlui && \
    git remote add origin https://github.com/xmlui-org/xmlui.git && \
    git fetch --depth=1 origin 559dd2d757eb9d99f093fd37ebea86bbd95975ea && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/xmlui
