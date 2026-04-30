FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        coreutils \
        findutils \
        gawk \
        bash \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4

WORKDIR /workspace

# Build a minimal git repository that mirrors the relevant parts of the
# ClickHouse tree at base commit cf5fb461472203d56bb0c169a61d194dd97fc2f2.
# The agent will edit ci/jobs/scripts/check_style/various_checks.sh to add
# a check that flags any git-tracked file larger than 5 MB unless whitelisted.
RUN mkdir -p /workspace/clickhouse/ci/jobs/scripts/check_style \
    && mkdir -p /workspace/clickhouse/tests/stress/keeper/workloads \
    && mkdir -p /workspace/clickhouse/tests/stress/keeper/scenarios

COPY various_checks.sh /workspace/clickhouse/ci/jobs/scripts/check_style/various_checks.sh
COPY core_no_faults.yaml /workspace/clickhouse/tests/stress/keeper/scenarios/core_no_faults.yaml

# Synthesise the 14 MB unused parquet (real file is binary; we only need its size
# for the size-check to detect it). The byte content is irrelevant — the script
# checks only `git ls-files` size, not magic bytes.
RUN dd if=/dev/zero of=/workspace/clickhouse/tests/stress/keeper/workloads/zookeeper_log.parquet \
        bs=1M count=14 status=none

# Add a small workload yaml so the directory has non-binary content too.
RUN printf '%s\n' \
    'name: prod_mix' \
    'concurrency: 64' \
    'connections:' \
    '  operation_timeout_ms: 30000' \
    > /workspace/clickhouse/tests/stress/keeper/workloads/prod_mix.yaml

RUN printf '%s\n' '# ClickHouse (test fixture)' > /workspace/clickhouse/README.md

# Initialise as a git repository so `git ls-files` works.
RUN cd /workspace/clickhouse \
    && chmod +x ci/jobs/scripts/check_style/various_checks.sh \
    && git init -q -b master \
    && git -c user.email=ci@example.com -c user.name=ci add -A \
    && git -c user.email=ci@example.com -c user.name=ci commit -q -m 'base'

RUN mkdir -p /logs/verifier
