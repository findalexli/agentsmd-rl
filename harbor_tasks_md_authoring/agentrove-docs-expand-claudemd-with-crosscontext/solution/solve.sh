#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agentrove

# Idempotency guard
if grep -qF "- When state is keyed by an input so render derives a `pending` flag as `stored." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -94,6 +94,10 @@
 - In shell command chains, use `&&` to gate dependent steps and wrap independent cleanup in `{ ...; }` when exit status must reflect earlier failures
 - When a shell/CLI command interpolates a path, confirm the cwd matches the path's basis — mixing repo-root-relative pathspecs with a nested cwd silently scopes operations wrong
 - When adding a bulk variant of a per-item operation, mirror every edge case (initial state, missing ref, newly-added vs tracked entries)
+- Route cross-context event handlers (SSE, WebSocket, pub/sub, stream callbacks) by the event's own identifiers (`envelope.chatId`), not hook-scoped ones — the latter silently misdirects off-screen updates
+- When a terminal/completion handler needs metadata about the completed entity, capture it at session/handle creation — don't resolve from the currently-viewed entity at completion time; off-screen completions land when the user has navigated elsewhere
+- For off-screen entities that need fresh state on next mount, patch the cache optimistically during the stream/mutation (`queryClient.setQueryData`) — `invalidateQueries` alone isn't enough since `useQuery` serves cached data on mount during the background refetch
+- Terminal-kind gating (cancelled vs complete) applies only to UI-side concerns (notifications, toasts). Cache invalidations for server-side state mutated during the turn must run regardless — cancelled runs still leave real side effects
 
 ## Naming Conventions
 
@@ -183,6 +187,7 @@
 - When state must reset on a prop/ID change, use a ref-based render check: `const prevRef = useRef(prop); if (prevRef.current !== prop) { prevRef.current = prop; setState(initial); }`
 - Distinguish "derived state" from "form state init" — if local state is a copy of server data the user then edits independently (secrets/settings forms), syncing via `useEffect` on query data change is correct
 - `useEffect` cleanup closures must not rely on hook-scoped utilities that close over the current entity ID when cleanup may serve sessions from a different entity — use refs or the underlying API (e.g., `queryClient.setQueryData` with `session.chatId`)
+- When state is keyed by an input so render derives a `pending` flag as `stored.input !== currentInput`, the effect must update state for every input value — bailing on falsy inputs (`if (!x) return`) leaves `stored.input` stale and the pending flag locked on forever
 
 ### Component Variants
 - Create explicit variant components instead of one with many boolean modes (e.g., `ThreadComposer`, `EditComposer` instead of `<Composer isThread isEditing />`)
PATCH

echo "Gold patch applied."
