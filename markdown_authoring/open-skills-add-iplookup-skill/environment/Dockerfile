FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/open-skills && \
    cd /workspace/open-skills && \
    git remote add origin https://github.com/besoeasy/open-skills.git && \
    git fetch --depth=1 origin 40635dbb2214a3ddf8752f9176660b5b17f8c856 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/open-skills
