FROM node:18-alpine

WORKDIR /workspace

RUN apk add --no-cache git bash curl

# Clone at base commit (before fix)
RUN git clone https://github.com/All-Hands-AI/OpenHands.git . && \
    git checkout b0d8244ad528a85d3b223478855b2a6cf8391d30

# Install frontend dependencies
RUN cd frontend && npm ci

CMD ["/bin/bash"]
