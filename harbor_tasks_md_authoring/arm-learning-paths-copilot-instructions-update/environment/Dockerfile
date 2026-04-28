FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/arm-learning-paths && \
    cd /workspace/arm-learning-paths && \
    git remote add origin https://github.com/ArmDeveloperEcosystem/arm-learning-paths.git && \
    git fetch --depth=1 origin 0f6eceafa0ef53f7949e6f311c320aa0cbf7622f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/arm-learning-paths
