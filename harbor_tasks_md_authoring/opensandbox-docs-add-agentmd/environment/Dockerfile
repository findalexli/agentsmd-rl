FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/opensandbox && \
    cd /workspace/opensandbox && \
    git remote add origin https://github.com/alibaba/OpenSandbox.git && \
    git fetch --depth=1 origin 1f4b978e73868681f50092506d6d6fb8dc717661 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opensandbox
