FROM python:3.12-slim

WORKDIR /workspace

# Install Go for building the project
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    gcc \
    make \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install specific Go version for reproducibility
RUN curl -fsSL https://go.dev/dl/go1.23.0.linux-amd64.tar.gz -o /tmp/go.tar.gz && \
    tar -C /usr/local -xzf /tmp/go.tar.gz && \
    rm /tmp/go.tar.gz
ENV PATH=/usr/local/go/bin:$PATH

# Clone Hugo repository (base commit for test isolation)
RUN git clone --depth 1 --filter=blob:none https://github.com/gohugoio/hugo.git hugo_repo
WORKDIR /workspace/hugo_repo
RUN git fetch --depth 1 origin cc338a9d4854c7e7273a5c3c8fee436c642f4dde && \
    git checkout cc338a9d4854c7e7273a5c3c8fee436c642f4dde

# Install Python testing deps
RUN pip install --no-cache-dir pytest==8.3.4

# Create logs directory
RUN mkdir -p /logs/verifier

COPY test.sh /tests/test.sh
RUN chmod +x /tests/test.sh
