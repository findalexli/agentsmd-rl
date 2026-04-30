FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/newrelic-dotnet-agent && \
    cd /workspace/newrelic-dotnet-agent && \
    git remote add origin https://github.com/newrelic/newrelic-dotnet-agent.git && \
    git fetch --depth=1 origin 9d0e57ed8c069c21b284b3695361b18fcfe66bdc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/newrelic-dotnet-agent
