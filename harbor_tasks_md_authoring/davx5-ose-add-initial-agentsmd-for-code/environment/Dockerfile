FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/davx5-ose && \
    cd /workspace/davx5-ose && \
    git remote add origin https://github.com/bitfireAT/davx5-ose.git && \
    git fetch --depth=1 origin b330ccf1ed0690cb57d3b9e104e66e90617ee623 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/davx5-ose
