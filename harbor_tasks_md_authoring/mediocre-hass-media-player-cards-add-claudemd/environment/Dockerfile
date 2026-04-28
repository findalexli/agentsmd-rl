FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/mediocre-hass-media-player-cards && \
    cd /workspace/mediocre-hass-media-player-cards && \
    git remote add origin https://github.com/antontanderup/mediocre-hass-media-player-cards.git && \
    git fetch --depth=1 origin 33b2f720ee2728c4aaf61a132774063ce90893af && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/mediocre-hass-media-player-cards
