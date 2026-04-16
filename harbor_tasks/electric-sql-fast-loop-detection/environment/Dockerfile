FROM elixir:1.19

RUN apt-get update && apt-get install -y --no-install-recommends git curl python3 python3-pip python3-pytest && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone with shallow history to reduce size
RUN git clone --depth 1 https://github.com/electric-sql/electric.git

WORKDIR /workspace/electric

# Checkout base commit (parent of merge)
RUN git fetch --depth 1 origin 4f55cef768a2933319c58c7e6275b7661030179c && \
    git checkout 4f55cef768a2933319c58c7e6275b7661030179c

WORKDIR /workspace/electric/packages/elixir-client

RUN mix local.hex --force && \
    mix local.rebar --force && \
    mix deps.get

RUN mkdir -p /logs/verifier

# Verify the image builds
RUN mix compile --warnings-as-errors || true