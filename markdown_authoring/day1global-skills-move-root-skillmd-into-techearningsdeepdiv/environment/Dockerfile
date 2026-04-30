FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/day1global-skills && \
    cd /workspace/day1global-skills && \
    git remote add origin https://github.com/star23/Day1Global-Skills.git && \
    git fetch --depth=1 origin 1e046528cd90850af3c9a5b6dc347c6025aa0e97 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/day1global-skills
