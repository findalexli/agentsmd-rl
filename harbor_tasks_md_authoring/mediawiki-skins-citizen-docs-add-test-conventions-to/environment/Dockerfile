FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mediawiki-skins-citizen && \
    cd /workspace/mediawiki-skins-citizen && \
    git remote add origin https://github.com/StarCitizenTools/mediawiki-skins-Citizen.git && \
    git fetch --depth=1 origin 2da2b9dbc340b5f6918d34a442c770caa8b51223 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mediawiki-skins-citizen
