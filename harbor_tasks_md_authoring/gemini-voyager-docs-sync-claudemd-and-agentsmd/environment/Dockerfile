FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gemini-voyager && \
    cd /workspace/gemini-voyager && \
    git remote add origin https://github.com/Nagi-ovo/gemini-voyager.git && \
    git fetch --depth=1 origin 8a870514d87206d5dfedc9b8ccf177c24a82e4ee && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gemini-voyager
