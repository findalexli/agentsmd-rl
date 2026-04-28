FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/policy-collection && \
    cd /workspace/policy-collection && \
    git remote add origin https://github.com/open-cluster-management-io/policy-collection.git && \
    git fetch --depth=1 origin d580fa54ff27353f70b619c2340a4281b1c6cea3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/policy-collection
