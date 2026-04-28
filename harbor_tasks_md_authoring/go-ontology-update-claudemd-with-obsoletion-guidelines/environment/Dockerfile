FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/go-ontology && \
    cd /workspace/go-ontology && \
    git remote add origin https://github.com/geneontology/go-ontology.git && \
    git fetch --depth=1 origin dc127356cc81d6c8a67684cdcf7b2894eb77339b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/go-ontology
