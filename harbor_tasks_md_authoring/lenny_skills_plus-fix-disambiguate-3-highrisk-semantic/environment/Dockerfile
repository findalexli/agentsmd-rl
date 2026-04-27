FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/lenny-skills-plus && \
    cd /workspace/lenny-skills-plus && \
    git remote add origin https://github.com/liqiongyu/lenny_skills_plus.git && \
    git fetch --depth=1 origin 242352d49bf6cd2c36ea4e122572f25e191a3356 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/lenny-skills-plus
