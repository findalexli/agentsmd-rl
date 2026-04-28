FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ingress-intel-total-conversion && \
    cd /workspace/ingress-intel-total-conversion && \
    git remote add origin https://github.com/IITC-CE/ingress-intel-total-conversion.git && \
    git fetch --depth=1 origin 8216b90a46002849c13c886642ee064fa82270a5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ingress-intel-total-conversion
