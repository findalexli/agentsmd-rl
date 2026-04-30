FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/azure-monitor-baseline-alerts && \
    cd /workspace/azure-monitor-baseline-alerts && \
    git remote add origin https://github.com/Azure/azure-monitor-baseline-alerts.git && \
    git fetch --depth=1 origin ebd04c54821e2128f54389b96f45efe952e7a446 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/azure-monitor-baseline-alerts
