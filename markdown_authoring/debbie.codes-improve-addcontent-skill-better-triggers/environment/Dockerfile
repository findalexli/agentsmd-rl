FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/debbie.codes && \
    cd /workspace/debbie.codes && \
    git remote add origin https://github.com/debs-obrien/debbie.codes.git && \
    git fetch --depth=1 origin 91a9a1741772483cc2155f0f08fccd3f12a02327 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/debbie.codes
