FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/swe-af && \
    cd /workspace/swe-af && \
    git remote add origin https://github.com/Agent-Field/SWE-AF.git && \
    git fetch --depth=1 origin 9c3443db27666a99ad6d212b6d9e62a08f364f5c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/swe-af
