FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/autoresearchclaw && \
    cd /workspace/autoresearchclaw && \
    git remote add origin https://github.com/aiming-lab/AutoResearchClaw.git && \
    git fetch --depth=1 origin 84c21b85ccd97b76cb693f013305ef85342f6706 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/autoresearchclaw
