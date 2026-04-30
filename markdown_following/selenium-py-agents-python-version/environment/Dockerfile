FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-ctrf==0.3.7

WORKDIR /workspace

RUN git init /workspace/selenium && \
    cd /workspace/selenium && \
    git remote add origin https://github.com/SeleniumHQ/selenium.git && \
    git fetch --depth=1 origin d4b49f5a60c8f5704b2ddd525395a6f1e13f73b3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier
