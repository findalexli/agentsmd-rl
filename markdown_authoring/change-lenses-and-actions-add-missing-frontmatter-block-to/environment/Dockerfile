FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/change-lenses-and-actions && \
    cd /workspace/change-lenses-and-actions && \
    git remote add origin https://github.com/johnpcutler/change-lenses-and-actions.git && \
    git fetch --depth=1 origin fd839ec081160d1dd3eedba7ec0b294124efd03f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/change-lenses-and-actions
