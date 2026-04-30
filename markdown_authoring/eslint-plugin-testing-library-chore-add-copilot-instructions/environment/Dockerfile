FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/eslint-plugin-testing-library && \
    cd /workspace/eslint-plugin-testing-library && \
    git remote add origin https://github.com/testing-library/eslint-plugin-testing-library.git && \
    git fetch --depth=1 origin 45515fc5f2f690a93521908555c416df93f0686d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/eslint-plugin-testing-library
