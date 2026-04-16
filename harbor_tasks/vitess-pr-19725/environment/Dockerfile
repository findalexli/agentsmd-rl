FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    patch \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none --depth=1 https://github.com/vitessio/vitess.git /workspace/vitess

WORKDIR /workspace/vitess

RUN git fetch --depth=1 origin 9a3646f7f16d38cec2efabc13cef5da800a72280 && \
    git checkout 9a3646f7f16d38cec2efabc13cef5da800a72280

RUN apt-get update && apt-get install -y --no-install-recommends \
    golang-go \
    && rm -rf /var/lib/apt/lists/*

COPY test.sh /tests/test.sh
COPY test_outputs.py /tests/test_outputs.py

RUN mkdir -p /logs/verifier

CMD ["bash"]