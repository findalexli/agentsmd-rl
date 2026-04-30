FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/autoskill && \
    cd /workspace/autoskill && \
    git remote add origin https://github.com/ECNU-ICALK/AutoSkill.git && \
    git fetch --depth=1 origin fe98df68c4d621e435eba01ee6eed46ee1d2ecce && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/autoskill
