FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git \
    && cd workers-sdk \
    && git checkout 9c5ebf56291199eeaec43513732fd3fa7fbd502d

RUN mkdir -p /logs/verifier

WORKDIR /workspace/workers-sdk
