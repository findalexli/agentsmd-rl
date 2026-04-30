FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hermes-agent && \
    cd /workspace/hermes-agent && \
    git remote add origin https://github.com/NousResearch/hermes-agent.git && \
    git fetch --depth=1 origin 4644f71faf3b3784b118db8af65cb5fcaeb40e38 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hermes-agent
