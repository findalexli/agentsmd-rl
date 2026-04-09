FROM mcr.microsoft.com/dotnet/sdk:9.0

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/dotnet/maui.git /workspace/maui && \
    cd /workspace/maui && \
    git checkout 260770c977f376c9b0190c03ed1a41920725f079 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/maui

# Pre-fetch NuGet packages for faster builds
RUN dotnet restore src/Essentials/src/Microsoft.Maui.Essentials.csproj 2>/dev/null || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
