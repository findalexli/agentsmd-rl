// TestResolveTransientManifestError verifies that a transient server error (5xx)
// from the /manifests/ endpoint does NOT cause containerd to fall back to the
// /blobs/ endpoint. Before this fix, a 500 from /manifests/ would cause Resolve()
// to silently retry via /blobs/, which returns "application/octet-stream" instead
// of a proper manifest media type — poisoning the descriptor and corrupting the
// local content store.
//
// The correct behavior is: 5xx from /manifests/ → return the server error, do NOT
// try /blobs/.
func TestResolveTransientManifestError(t *testing.T) {
	var (
		manifestCalled int
		blobsCalled    bool
		repo           = "test-repo"
		dgst           = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" // empty sha
	)

	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, "/manifests/"+dgst) {
			manifestCalled++
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		if strings.HasSuffix(r.URL.Path, "/blobs/"+dgst) {
			blobsCalled = true
			w.Header().Set("Content-Type", "application/octet-stream")
			w.Header().Set("Docker-Content-Digest", dgst)
			w.WriteHeader(http.StatusOK)
			return
		}
		if r.URL.Path == "/v2/" {
			w.WriteHeader(http.StatusOK)
			return
		}
		w.WriteHeader(http.StatusNotFound)
	}))
	defer ts.Close()

	resolver := NewResolver(ResolverOptions{
		Hosts: func(string) ([]RegistryHost, error) {
			return []RegistryHost{
				{
					Host:         ts.URL[len("http://"):],
					Scheme:       "http",
					Capabilities: HostCapabilityPull | HostCapabilityResolve,
				},
			}, nil
		},
	})

	ref := fmt.Sprintf("%s/%s@%s", ts.URL[len("http://"):], repo, dgst)
	_, _, err := resolver.Resolve(context.Background(), ref)

	if manifestCalled == 0 {
		t.Fatal("manifests endpoint was not called")
	}
	if blobsCalled {
		t.Error("blobs endpoint was called, but should not have been after a 500 on /manifests/")
	}
	if err == nil {
		t.Fatal("expected error from Resolve, but got nil")
	}

	// The error should surface the unexpected 500 status, not a generic "not found".
	var unexpectedStatus remoteerrors.ErrUnexpectedStatus
	if !errors.As(err, &unexpectedStatus) {
		t.Errorf("expected ErrUnexpectedStatus (from 500), got %T: %v", err, err)
	} else if unexpectedStatus.StatusCode != http.StatusInternalServerError {
		t.Errorf("expected status 500, got %d", unexpectedStatus.StatusCode)
	}
}

// TestResolve404ManifestFallback verifies that a 404 from /manifests/ DOES
// allow fallback to /blobs/. This preserves backward compatibility with
// non-standard registries that may only serve certain digests via /blobs/.
func TestResolve404ManifestFallback(t *testing.T) {
	var (
		manifestCalled bool
		blobsCalled    bool
		repo           = "test-repo"
		dgst           = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
	)

	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, "/manifests/"+dgst) {
			manifestCalled = true
			w.WriteHeader(http.StatusNotFound)
			return
		}
		if strings.HasSuffix(r.URL.Path, "/blobs/"+dgst) {
			blobsCalled = true
			w.Header().Set("Content-Type", "application/vnd.docker.distribution.manifest.v2+json")
			w.Header().Set("Docker-Content-Digest", dgst)
			w.WriteHeader(http.StatusOK)
			return
		}
		if r.URL.Path == "/v2/" {
			w.WriteHeader(http.StatusOK)
			return
		}
	}))
	defer ts.Close()

	resolver := NewResolver(ResolverOptions{
		Hosts: func(string) ([]RegistryHost, error) {
			return []RegistryHost{
				{
					Host:         ts.URL[len("http://"):],
					Scheme:       "http",
					Capabilities: HostCapabilityPull | HostCapabilityResolve,
				},
			}, nil
		},
	})

	ref := fmt.Sprintf("%s/%s@%s", ts.URL[len("http://"):], repo, dgst)
	_, desc, err := resolver.Resolve(context.Background(), ref)

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !manifestCalled {
		t.Error("manifests endpoint was not called")
	}
	if !blobsCalled {
		t.Error("blobs endpoint was not called on 404")
	}
	if desc.MediaType != "application/vnd.docker.distribution.manifest.v2+json" {
		t.Errorf("unexpected media type: %s", desc.MediaType)
	}
}
