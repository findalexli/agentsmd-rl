FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/hypershift && \
    cd /workspace/hypershift && \
    git remote add origin https://github.com/openshift/hypershift.git && \
    git fetch --depth=1 origin 491ccf53752f6f88a53fab3b12bfdd9048c6ea77 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/hypershift
