FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/teamcity-cli && \
    cd /workspace/teamcity-cli && \
    git remote add origin https://github.com/JetBrains/teamcity-cli.git && \
    git fetch --depth=1 origin 09111e96a4d6b2a1a4782b5da3a3a064378b27af && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/teamcity-cli
