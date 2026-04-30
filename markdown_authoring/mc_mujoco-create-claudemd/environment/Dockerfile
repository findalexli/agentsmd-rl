FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mc-mujoco && \
    cd /workspace/mc-mujoco && \
    git remote add origin https://github.com/rohanpsingh/mc_mujoco.git && \
    git fetch --depth=1 origin 3457911af9eeac3ada452aadd3b18dd9ad8306bf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mc-mujoco
