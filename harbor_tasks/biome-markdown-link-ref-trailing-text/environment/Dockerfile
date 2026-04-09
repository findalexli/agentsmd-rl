FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Install Rust (exact version from repo's rust-toolchain.toml)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- -y --default-toolchain 1.94.1
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/biomejs/biome.git /workspace/biome && \
    cd /workspace/biome && \
    git checkout aafca2d086eb24226a9cf1a69179561f70d02773 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/biome

# Create checker example used by test_outputs.py to probe parser behavior
RUN mkdir -p crates/biome_markdown_parser/examples && \
    cat > crates/biome_markdown_parser/examples/check_link_ref.rs <<'RUSTEOF'
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let input = &args[1];
    let parsed = biome_markdown_parser::parse_markdown(input);
    let output = format!("{:#?}", parsed.syntax());
    if output.contains("MdLinkReferenceDefinition") {
        println!("LINK_REF_DEF");
    } else {
        println!("NOT_LINK_REF_DEF");
    }
}
RUSTEOF

# Pre-fetch deps and pre-build for faster incremental compilation
RUN cargo fetch
RUN cargo build --example check_link_ref -p biome_markdown_parser 2>&1 || true
RUN cargo test -p biome_markdown_parser --no-run 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
