#!/bin/bash
set -euo pipefail

cd /workspace/hugo

# Idempotency guard: if patch already applied, exit
if grep -q "func (ns \*Namespace) ReplacePairs" tpl/strings/strings.go 2>/dev/null; then
    echo "Patch already applied — skipping"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tpl/strings/init.go b/tpl/strings/init.go
index 75473e4c156..d05133374cc 100644
--- a/tpl/strings/init.go
+++ b/tpl/strings/init.go
@@ -145,6 +145,20 @@ func init() {
 			},
 		)

+		ns.AddMethodMapping(ctx.ReplacePairs,
+			nil,
+			[][2]string{
+				{
+					`{{ "aab" | strings.ReplacePairs "a" "b" "b" "c" }}`,
+					`bbc`,
+				},
+				{
+					`{{ "aab" | strings.ReplacePairs (slice "a" "b" "b" "c") }}`,
+					`bbc`,
+				},
+			},
+		)
+
 		ns.AddMethodMapping(ctx.ReplaceRE,
 			[]string{"replaceRE"},
 			[][2]string{
diff --git a/tpl/strings/strings.go b/tpl/strings/strings.go
index f80fdd98bb7..24aff8588ba 100644
--- a/tpl/strings/strings.go
+++ b/tpl/strings/strings.go
@@ -23,6 +23,8 @@ import (
 	"unicode"
 	"unicode/utf8"

+	"github.com/gohugoio/hugo/common/hmaps"
+	"github.com/gohugoio/hugo/common/hreflect"
 	"github.com/gohugoio/hugo/common/text"
 	"github.com/gohugoio/hugo/deps"
 	"github.com/gohugoio/hugo/helpers"
@@ -34,14 +36,18 @@ import (

 // New returns a new instance of the strings-namespaced template functions.
 func New(d *deps.Deps) *Namespace {
-	return &Namespace{deps: d}
+	return &Namespace{
+		deps:          d,
+		replacerCache: hmaps.NewCacheWithOptions[string, *strings.Replacer](hmaps.CacheOptions{Size: 100}),
+	}
 }

 // Namespace provides template functions for the "strings" namespace.
 // Most functions mimic the Go stdlib, but the order of the parameters may be
 // different to ease their use in the Go template system.
 type Namespace struct {
-	deps *deps.Deps
+	deps          *deps.Deps
+	replacerCache *hmaps.Cache[string, *strings.Replacer]
 }

 // CountRunes returns the number of runes in s, excluding whitespace.
@@ -251,6 +257,61 @@ func (ns *Namespace) Replace(s, old, new any, limit ...any) (string, error) {
 	return strings.Replace(ss, so, sn, lim), nil
 }

+// ReplacePairs returns a copy of a string with multiple replacements performed
+// in a single pass. The last argument is the source string. Preceding arguments
+// are old/new string pairs, either as a slice or as individual arguments.
+func (ns *Namespace) ReplacePairs(args ...any) (string, error) {
+	if len(args) < 2 {
+		return "", fmt.Errorf("requires at least 2 arguments")
+	}
+
+	ss, err := cast.ToStringE(args[len(args)-1])
+	if err != nil {
+		return "", err
+	}
+
+	var p []string
+	if len(args) == 2 {
+		// slice form: ReplacePairs (slice "a" "b") "s"
+		if !hreflect.IsSlice(args[0]) {
+			return "", fmt.Errorf("with 2 arguments, the first must be a slice of replacement pairs, got %T", args[0])
+		}
+		p, err = cast.ToStringSliceE(args[0])
+		if err != nil {
+			return "", err
+		}
+	}
+	if p == nil {
+		// inline form: ReplacePairs "a" "b" "s"
+		p = make([]string, len(args)-1)
+		for i, v := range args[:len(args)-1] {
+			s, err := cast.ToStringE(v)
+			if err != nil {
+				return "", err
+			}
+			p[i] = s
+		}
+	}
+
+	if len(p) == 0 || ss == "" {
+		return ss, nil
+	}
+
+	if len(p)%2 != 0 {
+		return "", fmt.Errorf("uneven number of replacement pairs")
+	}
+
+	key := strings.Join(p, "\x00")
+	replacer, err := ns.replacerCache.GetOrCreate(key, func() (*strings.Replacer, error) {
+		return strings.NewReplacer(p...), nil
+	})
+	if err != nil {
+		return "", err
+	}
+
+	return replacer.Replace(ss), nil
+}
+
 // SliceString slices a string by specifying a half-open range with
 // two indices, start and end. 1 and 4 creates a slice including elements 1 through 3.
 // The end index can be omitted, it defaults to the string's length.
diff --git a/tpl/strings/strings_test.go b/tpl/strings/strings_test.go
index 0e6039ba137..d628ca5d362 100644
--- a/tpl/strings/strings_test.go
+++ b/tpl/strings/strings_test.go
@@ -15,6 +15,7 @@ package strings

 import (
 	"html/template"
+	stds "strings"
 	"testing"

 	qt "github.com/frankban/quicktest"
@@ -375,6 +376,91 @@ func TestReplace(t *testing.T) {
 	}
 }

+func TestReplacePairs(t *testing.T) {
+	t.Parallel()
+	c := qt.New(t)
+
+	for _, test := range []struct {
+		args   []any
+		expect string
+	}{
+		// slice form
+		{[]any{[]string{"a", "b"}, "aab"}, "bbb"},
+		{[]any{[]string{"a", "b", "b", "c"}, "aab"}, "bbc"},
+		{[]any{[]string{"app", "pear", "apple", "orange"}, "apple"}, "pearle"},
+		{[]any{[]string{}, "aab"}, "aab"},
+		{[]any{[]string{"remove-me", ""}, "text remove-me"}, "text "},
+		{[]any{[]string{"", "X"}, "ab"}, "XaXbX"},
+		{[]any{[]string{"a", "b"}, template.HTML("aab")}, "bbb"}, // template.HTML source
+		{[]any{[]string{"a", "b"}, 42}, "42"},                    // int source (cast: 42→"42")
+		{[]any{[]any{"a", "b"}, "s"}, "s"},                       // []any with all strings
+		{[]any{[]any{1, "one"}, "1abc"}, "oneabc"},               // []any with int pair (cast: 1→"1")
+		// inline form
+		{[]any{"a", "b", "aab"}, "bbb"},
+		{[]any{"a", "b", "b", "c", "aab"}, "bbc"},
+		{[]any{"app", "pear", "apple", "orange", "apple"}, "pearle"},
+		{[]any{"a", "b", ""}, ""},                      // empty source
+		{[]any{template.HTML("a"), "b", "aab"}, "bbb"}, // template.HTML pair
+		{[]any{1, "one", "1abc"}, "oneabc"},            // int pair (cast: 1→"1")
+	} {
+		result, err := ns.ReplacePairs(test.args...)
+		c.Assert(err, qt.IsNil)
+		c.Assert(result, qt.Equals, test.expect)
+	}
+
+	for _, test := range []struct {
+		args     []any
+		errMatch string
+	}{
+		{[]any{}, "requires at least 2"},                               // 0 args
+		{[]any{"s"}, "requires at least 2"},                            // 1 arg
+		{[]any{42, "s"}, "first must be a slice"},                      // 2 args: non-slice first arg
+		{[]any{"a", "s"}, "first must be a slice"},                     // 2 args: string first arg (not a slice)
+		{[]any{[]string{"a"}, "s"}, "uneven number"},                   // slice: odd pairs
+		{[]any{"a", "b", "c", "s"}, "uneven number"},                   // inline: 3 pairs
+		{[]any{[]any{tstNoStringer{}, "b"}, "s"}, "unable to cast"},    // non-castable slice element
+		{[]any{tstNoStringer{}, "b", "s"}, "unable to cast"},           // non-castable inline pair value
+		{[]any{[]string{"a", "b"}, tstNoStringer{}}, "unable to cast"}, // non-castable source
+	} {
+		_, err := ns.ReplacePairs(test.args...)
+		c.Assert(err, qt.ErrorMatches, ".*"+test.errMatch+".*")
+	}
+}
+
+func BenchmarkReplacePairs(b *testing.B) {
+	twoPairs := []string{"a", "A", "b", "B"}
+	threePairs := []string{"a", "A", "b", "B", "c", "C"}
+	s := "aabbcc"
+
+	b.Run("TwoPairs/cached", func(b *testing.B) {
+		b.ReportAllocs()
+		for b.Loop() {
+			ns.ReplacePairs(twoPairs, s)
+		}
+	})
+
+	b.Run("TwoPairs/uncached", func(b *testing.B) {
+		b.ReportAllocs()
+		for b.Loop() {
+			stds.NewReplacer(twoPairs...).Replace(s)
+		}
+	})
+
+	b.Run("ThreePairs/cached", func(b *testing.B) {
+		b.ReportAllocs()
+		for b.Loop() {
+			ns.ReplacePairs(threePairs, s)
+		}
+	})
+
+	b.Run("ThreePairs/uncached", func(b *testing.B) {
+		b.ReportAllocs()
+		for b.Loop() {
+			stds.NewReplacer(threePairs...).Replace(s)
+		}
+	})
+}
+
 func TestSliceString(t *testing.T) {
 	t.Parallel()
 	c := qt.New(t)
PATCH

echo "Patch applied successfully."
