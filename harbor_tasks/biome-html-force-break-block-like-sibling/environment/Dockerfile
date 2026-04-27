FROM rust:1.92.0-slim

# System deps for git, build tools (jemalloc-sys needs make+cc), python (test runner)
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        pkg-config \
        libssl-dev \
        build-essential \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Pinned Python deps (test runner only)
RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

# Add rustfmt + clippy components (slim image excludes them)
RUN rustup component add rustfmt clippy

# Clone biome at the base commit
ARG BIOME_COMMIT=883ea1d7748466dac8cec5bec7683b15ecfd37a1
RUN git clone --filter=blob:none https://github.com/biomejs/biome.git /workspace/biome \
    && cd /workspace/biome \
    && git checkout ${BIOME_COMMIT}

WORKDIR /workspace/biome

# Build the html formatter test binary at the base commit so the heavy
# dependency graph is cached in the docker image. Subsequent test runs after
# the agent's edits only need to recompile biome_html_formatter itself.
ENV CARGO_INCREMENTAL=0
ENV CARGO_TERM_COLOR=never

# Pre-place the new whitespace test fixtures so the gen_tests! proc-macro
# captures them in the compiled test binary. The .snap files are the
# expected formatted output the upstream PR shipped; tests compare the
# formatter's output against them. We re-copy these from /tests at test
# time to defend against agent tampering.
COPY fixtures/force-break-nontext-and-non-sensitive-sibling.html crates/biome_html_formatter/tests/specs/html/whitespace/
COPY fixtures/force-break-nontext-and-non-sensitive-sibling.html.snap crates/biome_html_formatter/tests/specs/html/whitespace/
COPY fixtures/no-break-display-none.html crates/biome_html_formatter/tests/specs/html/whitespace/
COPY fixtures/no-break-display-none.html.snap crates/biome_html_formatter/tests/specs/html/whitespace/

# Warm up the cache. First invocation inside a fresh container otherwise
# forces a full re-link (~55s) due to docker layer timestamp behaviour;
# running once during build commits warm artifacts into the image.
RUN cargo test -p biome_html_formatter --test spec_tests --locked formatter::html::html::whitespace::preserve_newline_after_element_html 2>&1 | tail -5

# Logs directory the harness reads from
RUN mkdir -p /logs/verifier
