FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone dagster repo at base commit (parent of merge commit)
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git \
    && cd dagster \
    && git checkout fe1beaad91470275c9fe30e0e12ef24d077cfa7b

# Install released dagster versions that are compatible with each other
# The base commit should be similar to a recent release
# Install exact ruff version required by the repo config
RUN pip install dagster dagster-aws pytest boto3 moto universal_pathlib ruff==0.15.0

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/dagster
