#!/usr/bin/env bash
# Build environment setup - runs during image build
set -e

echo "Setting up build environment for Move IDE task..."

# Install additional build dependencies if needed
apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    pkg-config \
    libssl-dev \
    || true

# Ensure Rust is properly set up
rustup default stable
rustup component add rustfmt clippy

echo "Build environment setup complete"
