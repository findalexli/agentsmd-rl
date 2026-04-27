FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/affiliate-skills && \
    cd /workspace/affiliate-skills && \
    git remote add origin https://github.com/Affitor/affiliate-skills.git && \
    git fetch --depth=1 origin 8850e158367d03edd0cf6013d9acd9831aaa046c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/affiliate-skills
