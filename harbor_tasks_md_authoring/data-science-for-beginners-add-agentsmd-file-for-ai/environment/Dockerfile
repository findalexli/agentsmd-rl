FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/data-science-for-beginners && \
    cd /workspace/data-science-for-beginners && \
    git remote add origin https://github.com/microsoft/Data-Science-For-Beginners.git && \
    git fetch --depth=1 origin c183f0ea28915e1338a44b361c435d9643e9cb13 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/data-science-for-beginners
