FROM golang:1.20

RUN apt-get update && apt-get install -y git python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone Hugo repo at base commit
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git && \
    cd hugo && \
    git checkout 44dc3847f4c91e86b1afa2350d42559bdecbaca9 && \
    # Fix go.mod to use Go 1.20 (compatible with our image)
    sed -i 's/^go 1.25.0$/go 1.20/' go.mod

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
