FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/phicookbook && \
    cd /workspace/phicookbook && \
    git remote add origin https://github.com/microsoft/PhiCookBook.git && \
    git fetch --depth=1 origin 8c41df9a9c89cbe741be45ef6f7304902b687239 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/phicookbook
