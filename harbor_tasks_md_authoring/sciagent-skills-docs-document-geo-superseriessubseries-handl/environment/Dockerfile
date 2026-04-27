FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sciagent-skills && \
    cd /workspace/sciagent-skills && \
    git remote add origin https://github.com/jaechang-hits/SciAgent-Skills.git && \
    git fetch --depth=1 origin 566e770ffd43d1ef44d29e99e7b257646b939e80 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sciagent-skills
