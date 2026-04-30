FROM eclipse-temurin:17.0.13_11-jdk-noble

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Pin pytest so the reward signal is stable across runs
RUN python3 -m pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4

WORKDIR /workspace

# Shallow-clone selenium at the base commit. The repo is large; we only
# need the Java sources (and root metadata) to scaffold the test.
RUN git clone --filter=blob:none --no-checkout https://github.com/SeleniumHQ/selenium.git /workspace/selenium \
    && cd /workspace/selenium \
    && git sparse-checkout init --cone \
    && git sparse-checkout set java AGENTS.md CLAUDE.md \
    && git checkout 89a97b7a7c901ce0d9ef561c531678baaa547a37

WORKDIR /workspace/selenium

RUN mkdir -p /logs/verifier

CMD ["/bin/bash"]
