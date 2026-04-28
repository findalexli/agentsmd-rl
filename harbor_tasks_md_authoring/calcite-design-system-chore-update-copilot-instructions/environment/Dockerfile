FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/calcite-design-system && \
    cd /workspace/calcite-design-system && \
    git remote add origin https://github.com/Esri/calcite-design-system.git && \
    git fetch --depth=1 origin 3b73344eebbe9eb1cdf2b9d18f11fa5e1a70f703 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/calcite-design-system
