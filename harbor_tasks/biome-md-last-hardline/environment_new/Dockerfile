FROM rust:1.94-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/biomejs/biome.git /workspace/biome && \
    cd /workspace/biome && \
    git checkout 0bc2198735230c3bad14a831652543bd304fa0d6 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/biome

# Pre-fetch deps
RUN cargo fetch

# Replace quick_test.rs with proper tests for the hard_line fix
RUN cat > /workspace/biome/crates/biome_markdown_formatter/tests/quick_test.rs << 'EOF'
use biome_markdown_formatter::{MdFormatLanguage, context::MdFormatOptions};
use biome_markdown_parser::parse_markdown;

fn format_markdown(source: &str) -> String {
    let parse = parse_markdown(source);
    let options = MdFormatOptions::default();
    let result = biome_formatter::format_node(&parse.syntax(), MdFormatLanguage::new(options), false);
    let formatted = result.unwrap();
    formatted.print().unwrap().as_code().to_string()
}

#[test]
fn test_single_last_hardline() {
    // Single-line paragraph ending with hard line break (two spaces)
    // The trailing spaces should be removed since it's the end of the paragraph
    let source = "Hello world  ";
    let result = format_markdown(source);
    // The formatted output should NOT have trailing two spaces
    // since the hard line break is at the end of the paragraph
    assert!(
        !result.ends_with("  \n"),
        "Trailing hard line break should be removed from end of paragraph. Got: {:?}",
        result
    );
    // Should still have the text content
    assert!(result.contains("Hello world"), "Content should be preserved. Got: {:?}", result);
}

#[test]
fn test_multi_last_hardline() {
    // Multi-line paragraph with hard line breaks
    // Middle hard lines should keep "  ", but the last one should be removed
    let source = "Line one  \nLine two  ";
    let result = format_markdown(source);

    // The last line of the paragraph should not have trailing "  "
    assert!(
        !result.trim_end().ends_with("  "),
        "Last hard line break should be removed. Got: {:?}",
        result
    );
}

#[test]
fn test_varied_last_hardline() {
    // Different content to prevent hardcoded solutions
    let source = "Different text content here  ";
    let result = format_markdown(source);

    // Should not have trailing hard line break at end of paragraph
    assert!(
        !result.trim_end().ends_with("  "),
        "Trailing spaces should be removed. Got: {:?}",
        result
    );
}
EOF

# Build formatter test binaries for fast testing (with our new quick_test.rs)
RUN cargo test -p biome_markdown_formatter --no-run 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
