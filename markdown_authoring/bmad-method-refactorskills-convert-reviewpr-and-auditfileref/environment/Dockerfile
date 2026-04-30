FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bmad-method && \
    cd /workspace/bmad-method && \
    git remote add origin https://github.com/bmad-code-org/BMAD-METHOD.git && \
    git fetch --depth=1 origin 276fcb1042e954044b445f4c488c70413d3e86c8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bmad-method
