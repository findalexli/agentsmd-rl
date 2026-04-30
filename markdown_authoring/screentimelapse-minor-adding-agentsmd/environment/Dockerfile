FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/screentimelapse && \
    cd /workspace/screentimelapse && \
    git remote add origin https://github.com/wkaisertexas/ScreenTimeLapse.git && \
    git fetch --depth=1 origin 46ab9d9fff1d359b5c91266b9f05caa052e72310 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/screentimelapse
