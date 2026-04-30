FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none --no-checkout \
    https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 2055f7743da5b0f578005adae60af31664b9d577

RUN pip install pytest==8.3.4

RUN mkdir -p /logs/verifier
