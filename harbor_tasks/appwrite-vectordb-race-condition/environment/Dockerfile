FROM php:8.3-cli

# Install git, python3, and composer dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git appwrite && \
    cd appwrite && \
    git checkout a5b0378138a6097e256a8d9553a18b892b6ba9ea

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
