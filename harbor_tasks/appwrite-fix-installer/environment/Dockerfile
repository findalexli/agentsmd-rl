FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    php \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth=1 https://github.com/appwrite/appwrite.git /workspace/appwrite \
    && cd /workspace/appwrite && git fetch --depth=1 origin ea032c28046c9f6cb1c2801fa80a9111f7e5fcd1:base \
    && git checkout base

WORKDIR /workspace/appwrite

RUN mkdir -p /logs/verifier

CMD ["bash"]