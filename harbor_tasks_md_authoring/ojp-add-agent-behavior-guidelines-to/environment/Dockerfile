FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ojp && \
    cd /workspace/ojp && \
    git remote add origin https://github.com/Open-J-Proxy/ojp.git && \
    git fetch --depth=1 origin 6e46a50e94f37284a2cbabee273296dfc05d8d0a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ojp
