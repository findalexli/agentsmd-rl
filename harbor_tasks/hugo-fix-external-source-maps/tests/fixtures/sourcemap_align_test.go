// Copyright 2026 The Hugo Authors. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package esbuild

import (
	"encoding/json"
	"testing"
)

// Verifies that fixSourceMap keeps the Sources slice and the SourcesContent
// slice index-aligned after the resolver has dropped some entries. This is
// the unit-level surface of the sourcemap.go fix in PR #14622.
func TestFixSourceMapKeepsSourcesContentAligned(t *testing.T) {
	input := `{"version":3,"sources":["a.css","b.css","c.css","d.css"],` +
		`"sourcesContent":["AA","BB","CC","DD"],` +
		`"mappings":"","names":[]}`

	// Resolver keeps the 1st and 3rd entries, drops the 2nd and 4th.
	resolve := func(s string) string {
		switch s {
		case "a.css", "c.css":
			return "/abs/" + s
		}
		return ""
	}

	out, err := fixSourceMap([]byte(input), resolve)
	if err != nil {
		t.Fatalf("fixSourceMap returned error: %v", err)
	}

	var sm sourceMap
	if err := json.Unmarshal(out, &sm); err != nil {
		t.Fatalf("unmarshal failed: %v\noutput: %s", err, string(out))
	}

	if got, want := len(sm.Sources), 2; got != want {
		t.Fatalf("len(Sources)=%d, want %d, output=%s", got, want, string(out))
	}
	if got, want := len(sm.SourcesContent), 2; got != want {
		t.Fatalf("len(SourcesContent)=%d, want %d, output=%s", got, want, string(out))
	}

	// SourcesContent must preserve alignment with Sources: index 0 → "AA",
	// index 1 → "CC". Pre-fix the slice was untouched (still 4 entries).
	if sm.SourcesContent[0] != "AA" {
		t.Fatalf("SourcesContent[0]=%q, want %q", sm.SourcesContent[0], "AA")
	}
	if sm.SourcesContent[1] != "CC" {
		t.Fatalf("SourcesContent[1]=%q, want %q", sm.SourcesContent[1], "CC")
	}
}

// When the input source map has no SourcesContent (legacy / minified case),
// fixSourceMap must still filter Sources without touching SourcesContent.
func TestFixSourceMapNoSourcesContent(t *testing.T) {
	input := `{"version":3,"sources":["a.css","b.css"],` +
		`"sourcesContent":null,` +
		`"mappings":"","names":[]}`

	resolve := func(s string) string {
		if s == "a.css" {
			return "/abs/a.css"
		}
		return ""
	}

	out, err := fixSourceMap([]byte(input), resolve)
	if err != nil {
		t.Fatalf("fixSourceMap returned error: %v", err)
	}
	var sm sourceMap
	if err := json.Unmarshal(out, &sm); err != nil {
		t.Fatalf("unmarshal failed: %v", err)
	}
	if got, want := len(sm.Sources), 1; got != want {
		t.Fatalf("len(Sources)=%d, want %d", got, want)
	}
	if len(sm.SourcesContent) != 0 {
		t.Fatalf("len(SourcesContent)=%d, want 0", len(sm.SourcesContent))
	}
}
