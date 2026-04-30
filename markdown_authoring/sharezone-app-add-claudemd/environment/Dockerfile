FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sharezone-app && \
    cd /workspace/sharezone-app && \
    git remote add origin https://github.com/SharezoneApp/sharezone-app.git && \
    git fetch --depth=1 origin 105b89dcb6d5fb70b0ddf7bf098136dee675ed13 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sharezone-app
