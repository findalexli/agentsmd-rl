FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/dash-skills && \
    cd /workspace/dash-skills && \
    git remote add origin https://github.com/kevmoo/dash_skills.git && \
    git fetch --depth=1 origin d868fad2132edd7c63b5b6e797c42827f28d2d8b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/dash-skills
