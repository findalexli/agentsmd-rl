FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dataverse-skills && \
    cd /workspace/dataverse-skills && \
    git remote add origin https://github.com/microsoft/Dataverse-skills.git && \
    git fetch --depth=1 origin 3c36b8d5ef41410b000872c697d9bb5138115e50 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dataverse-skills
