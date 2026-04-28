FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/magento-lts && \
    cd /workspace/magento-lts && \
    git remote add origin https://github.com/OpenMage/magento-lts.git && \
    git fetch --depth=1 origin deb951d0f498b2ccd82b7daf1b59233acce988dc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/magento-lts
