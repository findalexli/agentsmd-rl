FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/medusa-agent-skills && \
    cd /workspace/medusa-agent-skills && \
    git remote add origin https://github.com/medusajs/medusa-agent-skills.git && \
    git fetch --depth=1 origin 88adfce35705ae761a8b1792f166a625f4509d9a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/medusa-agent-skills
