FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/github-copilot-for-azure && \
    cd /workspace/github-copilot-for-azure && \
    git remote add origin https://github.com/microsoft/GitHub-Copilot-for-Azure.git && \
    git fetch --depth=1 origin 9040e3db4ba673a25f8fcf00b3fbd2fbaf2796f6 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/github-copilot-for-azure
