FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pydantic==2.12.5 \
    pytest==8.3.4 \
    pytest-json-ctrf==0.3.5

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/apache/superset.git /workspace/superset \
 && cd /workspace/superset \
 && git checkout 95f61bd223ee7f72893197c77ec73a06d225443b

WORKDIR /workspace/superset

RUN pip install --no-cache-dir -e .

RUN mkdir -p /logs/verifier
