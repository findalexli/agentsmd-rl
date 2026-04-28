FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/wordpress-ios && \
    cd /workspace/wordpress-ios && \
    git remote add origin https://github.com/wordpress-mobile/WordPress-iOS.git && \
    git fetch --depth=1 origin 37e5ce9fe639a6b175e64804aeec3601d6903215 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/wordpress-ios
