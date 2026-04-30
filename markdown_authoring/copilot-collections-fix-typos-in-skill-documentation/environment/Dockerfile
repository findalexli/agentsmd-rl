FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/copilot-collections && \
    cd /workspace/copilot-collections && \
    git remote add origin https://github.com/TheSoftwareHouse/copilot-collections.git && \
    git fetch --depth=1 origin 9ce7a06df20ac0f32f46f8d2566c3a3e2cd3d017 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/copilot-collections
