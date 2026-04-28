FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/web-dev-for-beginners && \
    cd /workspace/web-dev-for-beginners && \
    git remote add origin https://github.com/microsoft/Web-Dev-For-Beginners.git && \
    git fetch --depth=1 origin 7630e2fbabbe503532e2fcfea6d4b1242cf6a9bd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/web-dev-for-beginners
