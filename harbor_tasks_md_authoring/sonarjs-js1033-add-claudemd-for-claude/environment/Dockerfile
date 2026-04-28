FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sonarjs && \
    cd /workspace/sonarjs && \
    git remote add origin https://github.com/SonarSource/SonarJS.git && \
    git fetch --depth=1 origin 76ca2904d9bbaa10af4a2f5d63cfec8e3105955e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sonarjs
