FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cytoscape.js && \
    cd /workspace/cytoscape.js && \
    git remote add origin https://github.com/cytoscape/cytoscape.js.git && \
    git fetch --depth=1 origin 2c413460821c2898a6e7bd430d39fe5f16da2895 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cytoscape.js
