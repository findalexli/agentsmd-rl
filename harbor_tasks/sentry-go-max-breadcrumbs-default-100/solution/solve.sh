#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry-go

# Idempotency check: if patch is already applied, skip
if grep -q "defaultMaxBreadcrumbs = 100" client.go 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1533acc9e..c3ab9e5b0 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -1,5 +1,11 @@
 # Changelog

+## 0.36.0
+
+### Breaking Changes
+
+- Behavioral change for the `MaxBreadcrumbs` client option. Removed the hard limit of 100 breadcrumbs, allowing users to set a larger limit and also changed the default limit from 30 to 100 ([#1106](https://github.com/getsentry/sentry-go/pull/1106)))
+
 ## 0.35.3

 The Sentry SDK team is happy to announce the immediate availability of Sentry Go SDK v0.35.3.
diff --git a/client.go b/client.go
index 3a05846e9..2fb2f7184 100644
--- a/client.go
+++ b/client.go
@@ -20,19 +20,25 @@ import (
 // The identifier of the SDK.
 const sdkIdentifier = "sentry.go"

-// maxErrorDepth is the maximum number of errors reported in a chain of errors.
-// This protects the SDK from an arbitrarily long chain of wrapped errors.
-//
-// An additional consideration is that arguably reporting a long chain of errors
-// is of little use when debugging production errors with Sentry. The Sentry UI
-// is not optimized for long chains either. The top-level error together with a
-// stack trace is often the most useful information.
-const maxErrorDepth = 10
-
-// defaultMaxSpans limits the default number of recorded spans per transaction. The limit is
-// meant to bound memory usage and prevent too large transaction events that
-// would be rejected by Sentry.
-const defaultMaxSpans = 1000
+const (
+	// maxErrorDepth is the maximum number of errors reported in a chain of errors.
+	// This protects the SDK from an arbitrarily long chain of wrapped errors.
+	//
+	// An additional consideration is that arguably reporting a long chain of errors
+	// is of little use when debugging production errors with Sentry. The Sentry UI
+	// is not optimized for long chains either. The top-level error together with a
+	// stack trace is often the most useful information.
+	maxErrorDepth = 10
+
+	// defaultMaxSpans limits the default number of recorded spans per transaction. The limit is
+	// meant to bound memory usage and prevent too large transaction events that
+	// would be rejected by Sentry.
+	defaultMaxSpans = 1000
+
+	// defaultMaxBreadcrumbs is the default maximum number of breadcrumbs added to
+	// an event. Can be overwritten with the MaxBreadcrumbs option.
+	defaultMaxBreadcrumbs = 100
+)

 // hostname is the host name reported by the kernel. It is precomputed once to
 // avoid syscalls when capturing events.
diff --git a/hub.go b/hub.go
index 8aea27377..62983ffdf 100644
--- a/hub.go
+++ b/hub.go
@@ -18,14 +18,6 @@ const (
 	RequestContextKey = contextKey(2)
 )

-// defaultMaxBreadcrumbs is the default maximum number of breadcrumbs added to
-// an event. Can be overwritten with the maxBreadcrumbs option.
-const defaultMaxBreadcrumbs = 30
-
-// maxBreadcrumbs is the absolute maximum number of breadcrumbs added to an
-// event. The maxBreadcrumbs option cannot be set higher than this value.
-const maxBreadcrumbs = 100
-
 // currentHub is the initial Hub with no Client bound and an empty Scope.
 var currentHub = NewHub(nil, NewScope())

@@ -289,7 +281,7 @@ func (hub *Hub) AddBreadcrumb(breadcrumb *Breadcrumb, hint *BreadcrumbHint) {

 	// If there's no client, just store it on the scope straight away
 	if client == nil {
-		hub.Scope().AddBreadcrumb(breadcrumb, maxBreadcrumbs)
+		hub.Scope().AddBreadcrumb(breadcrumb, defaultMaxBreadcrumbs)
 		return
 	}

@@ -299,8 +291,6 @@ func (hub *Hub) AddBreadcrumb(breadcrumb *Breadcrumb, hint *BreadcrumbHint) {
 		return
 	case limit == 0:
 		limit = defaultMaxBreadcrumbs
-	case limit > maxBreadcrumbs:
-		limit = maxBreadcrumbs
 	}

 	if client.options.BeforeBreadcrumb != nil {
diff --git a/hub_test.go b/hub_test.go
index 184062179..ee98051ea 100644
--- a/hub_test.go
+++ b/hub_test.go
@@ -247,19 +247,6 @@ func TestAddBreadcrumbSkipAllBreadcrumbsIfMaxBreadcrumbsIsLessThanZero(t *testin
 	assertEqual(t, len(scope.breadcrumbs), 0)
 }

-func TestAddBreadcrumbShouldNeverExceedMaxBreadcrumbsConst(t *testing.T) {
-	hub, client, scope := setupHubTest()
-	client.options.MaxBreadcrumbs = 1000
-
-	breadcrumb := &Breadcrumb{Message: "Breadcrumb"}
-
-	for i := 0; i < 111; i++ {
-		hub.AddBreadcrumb(breadcrumb, nil)
-	}
-
-	assertEqual(t, len(scope.breadcrumbs), 100)
-}
-
 func TestAddBreadcrumbShouldWorkWithoutClient(t *testing.T) {
 	scope := NewScope()
 	hub := NewHub(nil, scope)
diff --git a/scope_test.go b/scope_test.go
index d11cd8ee4..c23163fcf 100644
--- a/scope_test.go
+++ b/scope_test.go
@@ -330,15 +330,15 @@ func TestScopeSetLevelOverrides(t *testing.T) {

 func TestAddBreadcrumbAddsBreadcrumb(t *testing.T) {
 	scope := NewScope()
-	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test"}, maxBreadcrumbs)
+	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test"}, defaultMaxBreadcrumbs)
 	assertEqual(t, []*Breadcrumb{{Timestamp: testNow, Message: "test"}}, scope.breadcrumbs)
 }

 func TestAddBreadcrumbAppendsBreadcrumb(t *testing.T) {
 	scope := NewScope()
-	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test1"}, maxBreadcrumbs)
-	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test2"}, maxBreadcrumbs)
-	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test3"}, maxBreadcrumbs)
+	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test1"}, defaultMaxBreadcrumbs)
+	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test2"}, defaultMaxBreadcrumbs)
+	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test3"}, defaultMaxBreadcrumbs)

 	assertEqual(t, []*Breadcrumb{
 		{Timestamp: testNow, Message: "test1"},
@@ -350,7 +350,7 @@ func TestAddBreadcrumbAppendsBreadcrumb(t *testing.T) {
 func TestAddBreadcrumbDefaultLimit(t *testing.T) {
 	scope := NewScope()
 	for i := 0; i < 101; i++ {
-		scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test"}, maxBreadcrumbs)
+		scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "test"}, defaultMaxBreadcrumbs)
 	}

 	if len(scope.breadcrumbs) != 100 {
@@ -361,7 +361,7 @@ func TestAddBreadcrumbDefaultLimit(t *testing.T) {
 func TestAddBreadcrumbAddsTimestamp(t *testing.T) {
 	scope := NewScope()
 	before := time.Now()
-	scope.AddBreadcrumb(&Breadcrumb{Message: "test"}, maxBreadcrumbs)
+	scope.AddBreadcrumb(&Breadcrumb{Message: "test"}, defaultMaxBreadcrumbs)
 	after := time.Now()
 	ts := scope.breadcrumbs[0].Timestamp

@@ -412,7 +412,7 @@ func TestScopeParentChangedInheritance(t *testing.T) {
 	clone.SetExtra("foo", "bar")
 	clone.SetLevel(LevelDebug)
 	clone.SetFingerprint([]string{"foo"})
-	clone.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "foo"}, maxBreadcrumbs)
+	clone.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "foo"}, defaultMaxBreadcrumbs)
 	clone.AddAttachment(&Attachment{Filename: "foo.txt", Payload: []byte("foo")})
 	clone.SetUser(User{ID: "foo"})
 	r1 := httptest.NewRequest("GET", "/foo", nil)
@@ -427,7 +427,7 @@ func TestScopeParentChangedInheritance(t *testing.T) {
 	scope.SetExtra("foo", "baz")
 	scope.SetLevel(LevelFatal)
 	scope.SetFingerprint([]string{"bar"})
-	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "bar"}, maxBreadcrumbs)
+	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "bar"}, defaultMaxBreadcrumbs)
 	scope.AddAttachment(&Attachment{Filename: "bar.txt", Payload: []byte("bar")})
 	scope.SetUser(User{ID: "bar"})
 	r2 := httptest.NewRequest("GET", "/bar", nil)
@@ -469,7 +469,7 @@ func TestScopeChildOverrideInheritance(t *testing.T) {
 	scope.SetExtra("foo", "baz")
 	scope.SetLevel(LevelFatal)
 	scope.SetFingerprint([]string{"bar"})
-	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "bar"}, maxBreadcrumbs)
+	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "bar"}, defaultMaxBreadcrumbs)
 	scope.AddAttachment(&Attachment{Filename: "bar.txt", Payload: []byte("bar")})
 	scope.SetUser(User{ID: "bar"})
 	r1 := httptest.NewRequest("GET", "/bar", nil)
@@ -488,7 +488,7 @@ func TestScopeChildOverrideInheritance(t *testing.T) {
 	clone.SetExtra("foo", "bar")
 	clone.SetLevel(LevelDebug)
 	clone.SetFingerprint([]string{"foo"})
-	clone.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "foo"}, maxBreadcrumbs)
+	clone.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "foo"}, defaultMaxBreadcrumbs)
 	clone.AddAttachment(&Attachment{Filename: "foo.txt", Payload: []byte("foo")})
 	clone.SetUser(User{ID: "foo"})
 	r2 := httptest.NewRequest("GET", "/foo", nil)
@@ -560,7 +560,7 @@ func TestClearAndReconfigure(t *testing.T) {
 	scope.SetExtra("foo", "bar")
 	scope.SetLevel(LevelDebug)
 	scope.SetFingerprint([]string{"foo"})
-	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "foo"}, maxBreadcrumbs)
+	scope.AddBreadcrumb(&Breadcrumb{Timestamp: testNow, Message: "foo"}, defaultMaxBreadcrumbs)
 	scope.AddAttachment(&Attachment{Filename: "foo.txt", Payload: []byte("foo")})
 	scope.SetUser(User{ID: "foo"})
 	r := httptest.NewRequest("GET", "/foo", nil)
PATCH

echo "Patch applied successfully."
