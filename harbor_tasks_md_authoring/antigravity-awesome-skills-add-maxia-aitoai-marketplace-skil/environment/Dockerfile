FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/antigravity-awesome-skills && \
    cd /workspace/antigravity-awesome-skills && \
    git remote add origin https://github.com/sickn33/antigravity-awesome-skills.git && \
    git fetch --depth=1 origin 25109a85e57d991e9330b72972fd3fa9e582ab22 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/antigravity-awesome-skills
