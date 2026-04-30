FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/alfanous && \
    cd /workspace/alfanous && \
    git remote add origin https://github.com/Alfanous-team/alfanous.git && \
    git fetch --depth=1 origin bcacc1472a3af715ace9a96fe4467babdff2dcb9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/alfanous
