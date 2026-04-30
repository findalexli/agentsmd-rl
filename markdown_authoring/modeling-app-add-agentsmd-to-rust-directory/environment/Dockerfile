FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/modeling-app && \
    cd /workspace/modeling-app && \
    git remote add origin https://github.com/KittyCAD/modeling-app.git && \
    git fetch --depth=1 origin 2cf11bf2d69f438dd9ef81b6710cf4f578304293 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/modeling-app
