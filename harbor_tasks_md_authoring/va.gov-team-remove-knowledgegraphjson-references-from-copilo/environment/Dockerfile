FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/va.gov-team && \
    cd /workspace/va.gov-team && \
    git remote add origin https://github.com/department-of-veterans-affairs/va.gov-team.git && \
    git fetch --depth=1 origin 0792a6e874a360b7ea0d3f7d0552d17a5e20b7cd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/va.gov-team
