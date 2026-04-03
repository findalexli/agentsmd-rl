#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry-go

# Idempotent: skip if already applied
if grep -q 'echo/v5' echo/go.mod 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/echo/README.md b/echo/README.md
index a03878f00..612c886f6 100644
--- a/echo/README.md
+++ b/echo/README.md
@@ -24,8 +24,8 @@ import (

     "github.com/getsentry/sentry-go"
     sentryecho "github.com/getsentry/sentry-go/echo"
-    "github.com/labstack/echo/v4"
-	"github.com/labstack/echo/v4/middleware"
+    "github.com/labstack/echo/v5"
+	"github.com/labstack/echo/v5/middleware"
 )

 // To initialize Sentry's handler, you need to initialize Sentry itself beforehand
@@ -45,7 +45,7 @@ app.Use(middleware.Recover())
 app.Use(sentryecho.New(sentryecho.Options{}))

 // Set up routes
-app.GET("/", func(ctx echo.Context) error {
+app.GET("/", func(ctx *echo.Context) error {
     return ctx.String(http.StatusOK, "Hello, World!")
 })

@@ -90,7 +90,7 @@ app.Use(sentryecho.New(sentryecho.Options{
 }))

 app.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
-	return func(ctx echo.Context) error {
+	return func(ctx *echo.Context) error {
 		if hub := sentryecho.GetHubFromContext(ctx); hub != nil {
 			hub.Scope().SetTag("someRandomTag", "maybeYouNeedIt")
 		}
@@ -98,7 +98,7 @@ app.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
 	}
 })

-app.GET("/", func(ctx echo.Context) error {
+app.GET("/", func(ctx *echo.Context) error {
 	if hub := sentryecho.GetHubFromContext(ctx); hub != nil {
 		hub.WithScope(func(scope *sentry.Scope) {
 			scope.SetTag("unwantedQuery", "someQueryDataMaybe")
@@ -108,7 +108,7 @@ app.GET("/", func(ctx echo.Context) error {
 	return ctx.String(http.StatusOK, "Hello, World!")
 })

-app.GET("/foo", func(ctx echo.Context) error {
+app.GET("/foo", func(ctx *echo.Context) error {
 	// sentryecho handler will catch it just fine. Also, because we attached "someRandomTag"
 	// in the middleware before, it will be sent through as well
 	panic("y tho")
diff --git a/echo/example_test.go b/echo/example_test.go
index e5a94c200..5e41eae35 100644
--- a/echo/example_test.go
+++ b/echo/example_test.go
@@ -6,13 +6,13 @@ import (

 	"github.com/getsentry/sentry-go"
 	sentryecho "github.com/getsentry/sentry-go/echo"
-	"github.com/labstack/echo/v4"
+	"github.com/labstack/echo/v5"
 )

 func ExampleGetSpanFromContext() {
 	router := echo.New()
 	router.Use(sentryecho.New(sentryecho.Options{}))
-	router.GET("/", func(c echo.Context) error {
+	router.GET("/", func(c *echo.Context) error {
 		expensiveThing := func(ctx context.Context) error {
 			span := sentry.StartTransaction(ctx, "expensive_thing")
 			defer span.Finish()
diff --git a/echo/sentryecho.go b/echo/sentryecho.go
index b892577c1..c219d2ac3 100644
--- a/echo/sentryecho.go
+++ b/echo/sentryecho.go
@@ -7,20 +7,21 @@ import (
 	"time"

 	"github.com/getsentry/sentry-go"
-	"github.com/labstack/echo/v4"
+	"github.com/getsentry/sentry-go/internal/debuglog"
+	"github.com/labstack/echo/v5"
 )

 const (
 	// sdkIdentifier is the identifier of the Echo SDK.
 	sdkIdentifier = "sentry.go.echo"

-	// valuesKey is used as a key to store the Sentry Hub instance on the  echo.Context.
+	// valuesKey is used as a key to store the Sentry Hub instance on the  *echo.Context.
 	valuesKey = "sentry"

-	// transactionKey is used as a key to store the Sentry transaction on the echo.Context.
+	// transactionKey is used as a key to store the Sentry transaction on the *echo.Context.
 	transactionKey = "sentry_transaction"

-	// errorKey is used as a key to store the error on the echo.Context.
+	// errorKey is used as a key to store the error on the *echo.Context.
 	errorKey = "error"
 )

@@ -57,7 +58,7 @@ func New(options Options) echo.MiddlewareFunc {
 }

 func (h *handler) handle(next echo.HandlerFunc) echo.HandlerFunc {
-	return func(ctx echo.Context) error {
+	return func(ctx *echo.Context) error {
 		hub := GetHubFromContext(ctx)
 		if hub == nil {
 			hub = sentry.CurrentHub().Clone()
@@ -93,15 +94,22 @@ func (h *handler) handle(next echo.HandlerFunc) echo.HandlerFunc {
 		transaction.SetData("http.request.method", r.Method)

 		defer func() {
-			status := ctx.Response().Status
+			var status int
+			if resp, err := echo.UnwrapResponse(ctx.Response()); err == nil && resp.Status != 0 {
+				status = resp.Status
+			}
 			if err := ctx.Get(errorKey); err != nil {
-				if httpError, ok := err.(*echo.HTTPError); ok {
-					status = httpError.Code
+				if coder, ok := err.(echo.HTTPStatusCoder); ok {
+					status = coder.StatusCode()
 				}
 			}

-			transaction.Status = sentry.HTTPtoSpanStatus(status)
-			transaction.SetData("http.response.status_code", status)
+			if status == 0 {
+				debuglog.Printf("sentryecho: unable to determine HTTP response status code")
+			} else {
+				transaction.Status = sentry.HTTPtoSpanStatus(status)
+				transaction.SetData("http.response.status_code", status)
+			}
 			transaction.Finish()
 		}()

@@ -135,22 +143,22 @@ func (h *handler) recoverWithSentry(hub *sentry.Hub, r *http.Request) {
 	}
 }

-// GetHubFromContext retrieves attached *sentry.Hub instance from echo.Context.
-func GetHubFromContext(ctx echo.Context) *sentry.Hub {
+// GetHubFromContext retrieves attached *sentry.Hub instance from *echo.Context.
+func GetHubFromContext(ctx *echo.Context) *sentry.Hub {
 	if hub, ok := ctx.Get(valuesKey).(*sentry.Hub); ok {
 		return hub
 	}
 	return nil
 }

-// SetHubOnContext attaches *sentry.Hub instance to echo.Context.
-func SetHubOnContext(ctx echo.Context, hub *sentry.Hub) {
+// SetHubOnContext attaches *sentry.Hub instance to *echo.Context.
+func SetHubOnContext(ctx *echo.Context, hub *sentry.Hub) {
 	ctx.Set(valuesKey, hub)
 }

-// GetSpanFromContext retrieves attached *sentry.Span instance from echo.Context.
-// If there is no transaction on echo.Context, it will return nil.
-func GetSpanFromContext(ctx echo.Context) *sentry.Span {
+// GetSpanFromContext retrieves attached *sentry.Span instance from *echo.Context.
+// If there is no transaction on *echo.Context, it will return nil.
+func GetSpanFromContext(ctx *echo.Context) *sentry.Span {
 	if span, ok := ctx.Get(transactionKey).(*sentry.Span); ok {
 		return span
 	}
diff --git a/echo/sentryecho_test.go b/echo/sentryecho_test.go
index 0c60cc38e..42a1782f2 100644
--- a/echo/sentryecho_test.go
+++ b/echo/sentryecho_test.go
@@ -15,7 +15,7 @@ import (
 	"github.com/getsentry/sentry-go/internal/testutils"
 	"github.com/google/go-cmp/cmp"
 	"github.com/google/go-cmp/cmp/cmpopts"
-	"github.com/labstack/echo/v4"
+	"github.com/labstack/echo/v5"
 )

 func TestIntegration(t *testing.T) {
@@ -37,7 +37,7 @@ func TestIntegration(t *testing.T) {
 			RoutePath:   "/panic/:id",
 			Method:      "GET",
 			WantStatus:  200,
-			Handler: func(c echo.Context) error {
+			Handler: func(c *echo.Context) error {
 				panic("test")
 			},
 			WantEvent: &sentry.Event{
@@ -114,7 +114,7 @@ func TestIntegration(t *testing.T) {
 			Method:      "POST",
 			WantStatus:  200,
 			Body:        "payload",
-			Handler: func(c echo.Context) error {
+			Handler: func(c *echo.Context) error {
 				hub := sentryecho.GetHubFromContext(c)
 				body, err := io.ReadAll(c.Request().Body)
 				if err != nil {
@@ -168,7 +168,7 @@ func TestIntegration(t *testing.T) {
 			RoutePath:   "/get",
 			Method:      "GET",
 			WantStatus:  200,
-			Handler: func(c echo.Context) error {
+			Handler: func(c *echo.Context) error {
 				hub := sentryecho.GetHubFromContext(c)
 				hub.CaptureMessage("get")
 				return c.JSON(http.StatusOK, map[string]string{"status": "get"})
@@ -215,7 +215,7 @@ func TestIntegration(t *testing.T) {
 			Method:      "POST",
 			WantStatus:  200,
 			Body:        largePayload,
-			Handler: func(c echo.Context) error {
+			Handler: func(c *echo.Context) error {
 				hub := sentryecho.GetHubFromContext(c)
 				body, err := io.ReadAll(c.Request().Body)
 				if err != nil {
@@ -270,7 +270,7 @@ func TestIntegration(t *testing.T) {
 			Method:      "POST",
 			WantStatus:  200,
 			Body:        "client sends, server ignores, SDK doesn't read",
-			Handler: func(c echo.Context) error {
+			Handler: func(c *echo.Context) error {
 				hub := sentryecho.GetHubFromContext(c)
 				hub.CaptureMessage("body ignored")
 				return nil
@@ -322,7 +322,7 @@ func TestIntegration(t *testing.T) {
 			RoutePath:   "/badreq",
 			Method:      "GET",
 			WantStatus:  400,
-			Handler: func(c echo.Context) error {
+			Handler: func(c *echo.Context) error {
 				return c.JSON(http.StatusBadRequest, map[string]string{"status": "bad_request"})
 			},
 			WantTransaction: &sentry.Event{
@@ -376,6 +376,9 @@ func TestIntegration(t *testing.T) {
 	router.Use(sentryecho.New(sentryecho.Options{}))

 	for _, tt := range tests {
+		if tt.Handler == nil {
+			continue // no route to register (e.g. 404 case: path /404/1 must not exist)
+		}
 		switch tt.Method {
 		case http.MethodGet:
 			router.GET(tt.RoutePath, tt.Handler)
@@ -499,7 +502,7 @@ func TestSetHubOnContext(t *testing.T) {

 	hub := sentry.CurrentHub().Clone()
 	router := echo.New()
-	router.GET("/set-hub", func(c echo.Context) error {
+	router.GET("/set-hub", func(c *echo.Context) error {
 		sentryecho.SetHubOnContext(c, hub)
 		retrievedHub := sentryecho.GetHubFromContext(c)
 		if retrievedHub == nil {
@@ -544,14 +547,14 @@ func TestGetSpanFromContext(t *testing.T) {
 	}

 	router := echo.New()
-	router.GET("/no-span", func(c echo.Context) error {
+	router.GET("/no-span", func(c *echo.Context) error {
 		span := sentryecho.GetSpanFromContext(c)
 		if span != nil {
 			t.Error("expecting span to be nil")
 		}
 		return c.NoContent(http.StatusOK)
 	})
-	router.GET("/with-span", func(c echo.Context) error {
+	router.GET("/with-span", func(c *echo.Context) error {
 		span := sentryecho.GetSpanFromContext(c)
 		if span == nil {
 			t.Error("expecting span to not be nil")
@@ -598,3 +601,47 @@ func TestGetSpanFromContext(t *testing.T) {
 		}
 	}
 }
+
+func TestUnwrapResponseError(t *testing.T) {
+	ch := make(chan *sentry.Event, 1)
+	if err := sentry.Init(sentry.ClientOptions{
+		EnableTracing:    true,
+		TracesSampleRate: 1.0,
+		BeforeSendTransaction: func(e *sentry.Event, _ *sentry.EventHint) *sentry.Event {
+			ch <- e
+			return e
+		},
+	}); err != nil {
+		t.Fatal(err)
+	}
+
+	router := echo.New()
+	router.Use(sentryecho.New(sentryecho.Options{}))
+	// ResponseWriter that does not implement Unwrap(), so echo.UnwrapResponse() returns an error.
+	router.GET("/unwrap-err", func(c *echo.Context) error {
+		c.SetResponse(&struct{ http.ResponseWriter }{c.Response()})
+		return c.JSON(http.StatusOK, "ok")
+	})
+
+	srv := httptest.NewServer(router)
+	defer srv.Close()
+
+	res, err := srv.Client().Get(srv.URL + "/unwrap-err")
+	if err != nil {
+		t.Fatal(err)
+	}
+	res.Body.Close()
+	if res.StatusCode != http.StatusOK {
+		t.Errorf("expected 200, got %d", res.StatusCode)
+	}
+
+	if !sentry.Flush(testutils.FlushTimeout()) {
+		t.Fatal("Flush timed out")
+	}
+	tx := <-ch
+
+	data := tx.Contexts["trace"]["data"].(map[string]any)
+	if _, ok := data["http.response.status_code"]; ok {
+		t.Errorf("when UnwrapResponse fails, expected no http.response.status_code to be set")
+	}
+}

PATCH

# Update go.mod to use echo/v5 and Go 1.25
cd echo
sed -i 's|go 1.24.0|go 1.25.0|' go.mod
sed -i 's|github.com/labstack/echo/v4 v4.10.1|github.com/labstack/echo/v5 v5.0.0|' go.mod

# Clean up old indirect deps and regenerate go.sum
go mod tidy

echo "Patch applied successfully."
