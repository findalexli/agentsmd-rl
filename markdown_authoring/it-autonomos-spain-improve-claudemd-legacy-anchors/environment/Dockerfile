FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/it-autonomos-spain && \
    cd /workspace/it-autonomos-spain && \
    git remote add origin https://github.com/v112263/it-autonomos-spain.git && \
    git fetch --depth=1 origin 1ac451a089977fc84c613db0aedcb3d02c063562 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/it-autonomos-spain
