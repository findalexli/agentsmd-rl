FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/rdf4j && \
    cd /workspace/rdf4j && \
    git remote add origin https://github.com/eclipse-rdf4j/rdf4j.git && \
    git fetch --depth=1 origin 824254524dd298ce947791c541a85745aad4601f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/rdf4j
