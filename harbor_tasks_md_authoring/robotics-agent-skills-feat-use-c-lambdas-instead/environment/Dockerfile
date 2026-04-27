FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/robotics-agent-skills && \
    cd /workspace/robotics-agent-skills && \
    git remote add origin https://github.com/arpitg1304/robotics-agent-skills.git && \
    git fetch --depth=1 origin 4a594d2380d81522cf285602b7357a80c63d78d9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/robotics-agent-skills
