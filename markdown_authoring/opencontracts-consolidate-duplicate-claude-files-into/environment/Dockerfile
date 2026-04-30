FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/opencontracts && \
    cd /workspace/opencontracts && \
    git remote add origin https://github.com/Open-Source-Legal/OpenContracts.git && \
    git fetch --depth=1 origin 9b60c29794a4e3af7062309b7a541760b893b823 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencontracts
