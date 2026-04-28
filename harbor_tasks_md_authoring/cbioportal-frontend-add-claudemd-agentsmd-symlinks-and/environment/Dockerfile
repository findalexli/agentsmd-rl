FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cbioportal-frontend && \
    cd /workspace/cbioportal-frontend && \
    git remote add origin https://github.com/cBioPortal/cbioportal-frontend.git && \
    git fetch --depth=1 origin ee62354fb3bbd81ff71466091d83539bb4de2d56 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cbioportal-frontend
