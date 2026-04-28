FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/chart-visualization-skills && \
    cd /workspace/chart-visualization-skills && \
    git remote add origin https://github.com/antvis/chart-visualization-skills.git && \
    git fetch --depth=1 origin 79513ce84a523162ddfd7270e6abbbc10764ab1e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/chart-visualization-skills
