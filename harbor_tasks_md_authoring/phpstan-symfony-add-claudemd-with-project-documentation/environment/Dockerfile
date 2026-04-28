FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/phpstan-symfony && \
    cd /workspace/phpstan-symfony && \
    git remote add origin https://github.com/phpstan/phpstan-symfony.git && \
    git fetch --depth=1 origin b8d8116ad2e02544e5480baabc8fc911f045aac0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/phpstan-symfony
