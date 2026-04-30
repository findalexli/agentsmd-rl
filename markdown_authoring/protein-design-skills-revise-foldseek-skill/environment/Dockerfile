FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/protein-design-skills && \
    cd /workspace/protein-design-skills && \
    git remote add origin https://github.com/adaptyvbio/protein-design-skills.git && \
    git fetch --depth=1 origin da04082330201058f0a72f72cc39cec6ddad46bd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/protein-design-skills
