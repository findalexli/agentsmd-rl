#!/bin/bash
set -e

cd /workspace/moby

# Check if already applied (idempotency)
if grep -q 'resolveProgressDone := progress.OneOff(ctx, "resolve "+p.src.Reference.String())' daemon/internal/builder-next/adapters/containerimage/pull.go; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -v -
diff --git a/daemon/internal/builder-next/adapters/containerimage/pull.go b/daemon/internal/builder-next/adapters/containerimage/pull.go
index 01b26b58024fa..31a8369445bae 100644
--- a/daemon/internal/builder-next/adapters/containerimage/pull.go
+++ b/daemon/internal/builder-next/adapters/containerimage/pull.go
@@ -347,7 +347,7 @@ func (p *puller) resolveLocal() {

 func (p *puller) resolve(ctx context.Context, jobCtx solver.JobContext) error {
 	_, err := p.g.Do(ctx, "", func(ctx context.Context) (_ struct{}, retErr error) {
-		resolveProgressDone := oneOffProgress(ctx, "resolve "+p.src.Reference.String())
+		resolveProgressDone := progress.OneOff(ctx, "resolve "+p.src.Reference.String())
 		defer func() {
 			_ = resolveProgressDone(retErr)
 		}()
@@ -901,23 +901,6 @@ type statusInfo struct {
 	UpdatedAt time.Time
 }

-func oneOffProgress(ctx context.Context, id string) func(err error) error {
-	pw, _, _ := progress.NewFromContext(ctx)
-	s := time.Now()
-	st := progress.Status{
-		Started: &s,
-	}
-	_ = pw.Write(id, st)
-	return func(err error) error {
-		// TODO: set error on status
-		c := time.Now()
-		st.Completed = &c
-		_ = pw.Write(id, st)
-		_ = pw.Close()
-		return err
-	}
-}
-
 // cacheKeyFromConfig returns a stable digest from image config. If image config
 // is a known oci image we will use chainID of layers.
 func cacheKeyFromConfig(dt []byte) digest.Digest {
diff --git a/daemon/internal/builder-next/exporter/mobyexporter/export.go b/daemon/internal/builder-next/exporter/mobyexporter/export.go
index b49794487ae65..abde0751b7c95 100644
--- a/daemon/internal/builder-next/exporter/mobyexporter/export.go
+++ b/daemon/internal/builder-next/exporter/mobyexporter/export.go
@@ -15,6 +15,7 @@ import (
 	"github.com/moby/buildkit/exporter/containerimage"
 	"github.com/moby/buildkit/exporter/containerimage/exptypes"
 	"github.com/moby/buildkit/util/leaseutil"
+	"github.com/moby/buildkit/util/progress"
 	"github.com/moby/moby/v2/daemon/internal/image"
 	"github.com/moby/moby/v2/daemon/internal/layer"
 	"github.com/opencontainers/go-digest"
@@ -137,7 +138,7 @@ func (e *imageExporterInstance) Export(ctx context.Context, inp *exporter.Source

 	var diffs []digest.Digest
 	if ref != nil {
-		layersDone := oneOffProgress(ctx, "exporting layers")
+		layersDone := progress.OneOff(ctx, "exporting layers")

 		if err := ref.Finalize(ctx); err != nil {
 			return nil, nil, nil, layersDone(err)
@@ -193,7 +194,7 @@ func (e *imageExporterInstance) Export(ctx context.Context, inp *exporter.Source

 	configDigest := digest.FromBytes(config)

-	configDone := oneOffProgress(ctx, fmt.Sprintf("writing image %s", configDigest))
+	configDone := progress.OneOff(ctx, fmt.Sprintf("writing image %s", configDigest))
 	id, err := e.opt.ImageStore.Create(config)
 	if err != nil {
 		return nil, nil, nil, configDone(err)
@@ -204,7 +205,7 @@ func (e *imageExporterInstance) Export(ctx context.Context, inp *exporter.Source
 	for _, targetName := range e.targetNames {
 		names = append(names, targetName.String())
 		if e.opt.ImageTagger != nil {
-			tagDone := oneOffProgress(ctx, "naming to "+targetName.String())
+			tagDone := progress.OneOff(ctx, "naming to "+targetName.String())
 			if err := e.opt.ImageTagger.TagImage(ctx, image.ID(digest.Digest(id)), targetName); err != nil {
 				return nil, nil, nil, tagDone(err)
 			}
diff --git a/daemon/internal/builder-next/exporter/mobyexporter/writer.go b/daemon/internal/builder-next/exporter/mobyexporter/writer.go
index 91501a4c3b5bb..df00982ac5fb6 100644
--- a/daemon/internal/builder-next/exporter/mobyexporter/writer.go
+++ b/daemon/internal/builder-next/exporter/mobyexporter/writer.go
@@ -9,7 +9,6 @@ import (
 	"github.com/containerd/platforms"
 	"github.com/moby/buildkit/cache"
 	"github.com/moby/buildkit/exporter/containerimage/exptypes"
-	"github.com/moby/buildkit/util/progress"
 	"github.com/moby/buildkit/util/system"
 	"github.com/opencontainers/go-digest"
 	ocispec "github.com/opencontainers/image-spec/specs-go/v1"
@@ -205,20 +204,3 @@ func getRefMetadata(ref cache.ImmutableRef, limit int) []refMetadata {
 	}
 	return metas
 }
-
-func oneOffProgress(ctx context.Context, id string) func(err error) error {
-	pw, _, _ := progress.NewFromContext(ctx)
-	now := time.Now()
-	st := progress.Status{
-		Started: &now,
-	}
-	_ = pw.Write(id, st)
-	return func(err error) error {
-		// TODO: set error on status
-		now := time.Now()
-		st.Completed = &now
-		_ = pw.Write(id, st)
-		_ = pw.Close()
-		return err
-	}
-}
diff --git a/daemon/internal/builder-next/worker/worker.go b/daemon/internal/builder-next/worker/worker.go
index 95a80072109e1..5535dc3b8977a 100644
--- a/daemon/internal/builder-next/worker/worker.go
+++ b/daemon/internal/builder-next/worker/worker.go
@@ -603,7 +603,7 @@ func (ld *layerDescriptor) DiffID() (layer.DiffID, error) {
 }

 func (ld *layerDescriptor) Download(ctx context.Context, progressOutput pkgprogress.Output) (io.ReadCloser, int64, error) {
-	done := oneOffProgress(ld.pctx, fmt.Sprintf("pulling %s", ld.desc.Digest))
+	done := progress.OneOff(ld.pctx, fmt.Sprintf("pulling %s", ld.desc.Digest))

 	// TODO should this write output to progressOutput? Or use something similar to loggerFromContext()? see https://github.com/moby/buildkit/commit/aa29e7729464f3c2a773e27795e584023c751cb8
 	discardLogs := func(_ []byte) {}
@@ -653,23 +653,6 @@ func getLayers(ctx context.Context, descs []ocispec.Descriptor) ([]rootfs.Layer,
 	return layers, nil
 }

-func oneOffProgress(ctx context.Context, id string) func(err error) error {
-	pw, _, _ := progress.NewFromContext(ctx)
-	s := time.Now()
-	st := progress.Status{
-		Started: &s,
-	}
-	_ = pw.Write(id, st)
-	return func(err error) error {
-		// TODO: set error on status
-		c := time.Now()
-		st.Completed = &c
-		_ = pw.Write(id, st)
-		_ = pw.Close()
-		return err
-	}
-}
-
 type emptyProvider struct{}

 func (p *emptyProvider) ReaderAt(ctx context.Context, dec ocispec.Descriptor) (content.ReaderAt, error) {
PATCH

echo "Patch applied successfully"
