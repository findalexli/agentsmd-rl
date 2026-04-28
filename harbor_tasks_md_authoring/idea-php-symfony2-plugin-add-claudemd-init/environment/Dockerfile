FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/idea-php-symfony2-plugin && \
    cd /workspace/idea-php-symfony2-plugin && \
    git remote add origin https://github.com/Haehnchen/idea-php-symfony2-plugin.git && \
    git fetch --depth=1 origin 1c64ab1399580d945f0e6714b3e85253f38511e4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/idea-php-symfony2-plugin
