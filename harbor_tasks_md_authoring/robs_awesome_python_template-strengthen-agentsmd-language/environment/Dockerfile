FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/robs-awesome-python-template && \
    cd /workspace/robs-awesome-python-template && \
    git remote add origin https://github.com/tedivm/robs_awesome_python_template.git && \
    git fetch --depth=1 origin ba384dbe644a571ef22862e524ee1b414ce91321 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/robs-awesome-python-template
