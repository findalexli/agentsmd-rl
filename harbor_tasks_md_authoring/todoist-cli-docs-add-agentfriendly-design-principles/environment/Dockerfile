FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/todoist-cli && \
    cd /workspace/todoist-cli && \
    git remote add origin https://github.com/Doist/todoist-cli.git && \
    git fetch --depth=1 origin 8bc7fa3c05e11a6d659cc657a62473e3a29cee2a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/todoist-cli
