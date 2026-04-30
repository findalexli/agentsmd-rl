FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/surveysolutions && \
    cd /workspace/surveysolutions && \
    git remote add origin https://github.com/surveysolutions/surveysolutions.git && \
    git fetch --depth=1 origin e74176a5f750ca2bf2874d33e64a3e6964833e89 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/surveysolutions
