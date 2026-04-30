FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cargo-semver-checks && \
    cd /workspace/cargo-semver-checks && \
    git remote add origin https://github.com/obi1kenobi/cargo-semver-checks.git && \
    git fetch --depth=1 origin 473153312c2415203368125bf1267cc8eb4db28e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cargo-semver-checks
