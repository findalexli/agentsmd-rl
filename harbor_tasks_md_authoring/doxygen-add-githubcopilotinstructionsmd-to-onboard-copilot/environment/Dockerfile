FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/doxygen && \
    cd /workspace/doxygen && \
    git remote add origin https://github.com/doxygen/doxygen.git && \
    git fetch --depth=1 origin 0e0bf0380af433ff732efeb3b9e3642aea74e5d0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/doxygen
