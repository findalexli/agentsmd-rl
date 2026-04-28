FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nitrite-java && \
    cd /workspace/nitrite-java && \
    git remote add origin https://github.com/nitrite/nitrite-java.git && \
    git fetch --depth=1 origin 34d31de84b8d0990716c2318b86146789beeb01b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nitrite-java
