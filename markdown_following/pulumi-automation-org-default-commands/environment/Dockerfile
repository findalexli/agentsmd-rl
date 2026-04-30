FROM golang:1.25-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        git \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Clone the Pulumi repo at the base commit (parent of merge for PR #22436).
WORKDIR /workspace
RUN git init /workspace/pulumi && \
    cd /workspace/pulumi && \
    git remote add origin https://github.com/pulumi/pulumi.git && \
    git fetch --depth=1 origin 40fd96368b6bab557b45747a4e4cb5a9082a7340 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/pulumi

# Pre-fetch Go module deps for sdk/go so tests can run offline.
RUN cd sdk/go && go mod download

# Set up a Python venv with the Pulumi Python SDK installed in editable mode
# plus pytest.
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip==25.2 \
    && pip install \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        protobuf==5.29.3 \
        grpcio==1.71.0 \
        dill==0.4.0 \
        semver==3.0.4 \
        pyyaml==6.0.2 \
        debugpy==1.8.14 \
        packaging==26.0 \
        opentelemetry-api==1.28.2 \
        opentelemetry-sdk==1.28.2 \
        opentelemetry-exporter-otlp-proto-grpc==1.28.2 \
        opentelemetry-instrumentation-grpc==0.49b2

# Install the Pulumi Python SDK as a no-deps editable install (we already
# pinned compatible versions of every dep above).
RUN pip install --no-deps -e ./sdk/python

RUN mkdir -p /logs/verifier
