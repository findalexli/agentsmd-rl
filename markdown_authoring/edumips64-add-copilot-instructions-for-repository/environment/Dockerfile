FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/edumips64 && \
    cd /workspace/edumips64 && \
    git remote add origin https://github.com/EduMIPS64/edumips64.git && \
    git fetch --depth=1 origin 22675962f0916f7b76668042bdc4b1c0c62bee36 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/edumips64
