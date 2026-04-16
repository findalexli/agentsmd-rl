FROM golang:1.25-alpine

# Install dependencies including gcc for CGO/race detector
RUN apk add --no-cache git bash curl python3 py3-pip gcc musl-dev

# Set up working directory
WORKDIR /workspace/moby

# Clone the repo at base commit
ARG BASE_COMMIT=20d257b457d24d222bd7fc3a5781d09abf23f989
RUN git clone --filter=blob:none https://github.com/moby/moby.git /workspace/moby && \
    git checkout ${BASE_COMMIT}

# Add the race test to utils_test.go (this test was added in the PR)
RUN cat >> /workspace/moby/client/utils_test.go << 'EOF'

func TestNewCancelReadCloserRace(t *testing.T) {
	for range 1000 {
		ctx, cancel := context.WithCancel(t.Context())
		cancel()

		_ = newCancelReadCloser(ctx, io.NopCloser(strings.NewReader("")))
	}
}
EOF

# Fix imports - add context, io, strings if missing
RUN sed -i 's/"testing"/"context"\n\t"io"\n\t"strings"\n\n\t"testing"/' /workspace/moby/client/utils_test.go

# Install Python packages for testing
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
