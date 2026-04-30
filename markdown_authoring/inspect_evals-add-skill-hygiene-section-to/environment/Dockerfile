FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/inspect-evals && \
    cd /workspace/inspect-evals && \
    git remote add origin https://github.com/UKGovernmentBEIS/inspect_evals.git && \
    git fetch --depth=1 origin 10acfda956d1d4234fe7e8eb1600d348e9a2e5d7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/inspect-evals
