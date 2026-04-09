"""
Task: goose-remove-closedsenderdone-and-closedreceiverdone-states
Repo: goose-lang/goose @ 16144157af4b64fe96deac36fcd2638503fdc2e2
PR:   130

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/goose"
CHANNEL_FILE = f"{REPO}/model/channel/channel.go"


def _run_go(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Go code via 'go run' in the repo directory."""
    script = Path(REPO) / "_eval_tmp.go"
    script.write_text(code)
    try:
        return subprocess.run(
            ["go", "run", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _check_go_build() -> subprocess.CompletedProcess:
    """Check if the channel package builds without errors."""
    return subprocess.run(
        ["go", "build", "./model/channel/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / compilation
# ---------------------------------------------------------------------------

def test_go_syntax_valid():
    """Modified Go files parse without syntax errors."""
    r = _check_go_build()
    assert r.returncode == 0, f"Go build failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral changes
# ---------------------------------------------------------------------------

def test_new_states_added():
    """Channel model uses new explicit state constants (SndWait, RcvWait, SndDone, RcvDone, Closed)."""
    r = subprocess.run(
        ["go", "run", "-"],
        input=f"""package main
import (
    "fmt"
    "os"
    "strings"
)

func main() {{
    content, err := os.ReadFile("{CHANNEL_FILE}")
    if err != nil {{
        fmt.Println("FAIL: Cannot read channel.go:", err)
        os.Exit(1)
    }}
    src := string(content)

    // Check for new explicit state constants
    requiredStates := []string{{"SndWait", "RcvWait", "SndDone", "RcvDone", "Closed", "Buffered", "Idle"}}
    for _, state := range requiredStates {{
        if !strings.Contains(src, state + "  OfferState") && !strings.Contains(src, state + " OfferState") {{
            fmt.Println("FAIL: Missing state constant:", state)
            os.Exit(1)
        }}
    }}

    fmt.Println("PASS: All new state constants found")
}}
""",
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_old_states_removed():
    """Old state constants (offer, accepted) removed from OfferState enum."""
    r = subprocess.run(
        ["go", "run", "-"],
        input=f"""package main
import (
    "fmt"
    "os"
    "strings"
)

func main() {{
    content, err := os.ReadFile("{CHANNEL_FILE}")
    if err != nil {{
        fmt.Println("FAIL: Cannot read channel.go:", err)
        os.Exit(1)
    }}
    src := string(content)

    // Old state constants should NOT exist (case-insensitive check)
    forbidden := []string{{"offer OfferState", "accepted OfferState", "idle OfferState = 0"}}
    for _, f := range forbidden {{
        if strings.Contains(src, f) {{
            fmt.Println("FAIL: Old state constant still present:", f)
            os.Exit(1)
        }}
    }}

    // Also check that 'offer' and 'accepted' are not used as state names in const block
    // (they might appear in comments, so we check the const block specifically)
    if strings.Contains(src, "offer    OfferState") || strings.Contains(src, "accepted OfferState") {{
        fmt.Println("FAIL: Old state constants offer/accepted still present")
        os.Exit(1)
    }}

    fmt.Println("PASS: Old state constants removed")
}}
""",
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_send_refactored():
    """Send method refactored to use TrySend in for loop instead of Select1."""
    r = subprocess.run(
        ["go", "run", "-"],
        input=f"""package main
import (
    "fmt"
    "os"
    "strings"
)

func main() {{
    content, err := os.ReadFile("{CHANNEL_FILE}")
    if err != nil {{
        fmt.Println("FAIL: Cannot read channel.go:", err)
        os.Exit(1)
    }}
    src := string(content)

    // Should use TrySend in a for loop
    if !strings.Contains(src, "for !c.TrySend(v, true)") {{
        fmt.Println("FAIL: Send does not use TrySend in for loop pattern")
        os.Exit(1)
    }}

    // Should NOT use Select1 anymore
    if strings.Contains(src, "Select1(sendCase") {{
        fmt.Println("FAIL: Send still uses old Select1 pattern")
        os.Exit(1)
    }}

    // Should NOT create sendCase
    if strings.Contains(src, "NewSendCase") {{
        fmt.Println("FAIL: Send still creates sendCase")
        os.Exit(1)
    }}

    fmt.Println("PASS: Send method refactored correctly")
}}
""",
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_receive_refactored():
    """Receive method refactored to use TryReceive in for loop instead of Select1."""
    r = subprocess.run(
        ["go", "run", "-"],
        input=f"""package main
import (
    "fmt"
    "os"
    "strings"
)

func main() {{
    content, err := os.ReadFile("{CHANNEL_FILE}")
    if err != nil {{
        fmt.Println("FAIL: Cannot read channel.go:", err)
        os.Exit(1)
    }}
    src := string(content)

    // Should use TryReceive in a for loop
    if !strings.Contains(src, "success, v, ok := c.TryReceive(true)") {{
        fmt.Println("FAIL: Receive does not use TryReceive in for loop pattern")
        os.Exit(1)
    }}

    // Should NOT use Select1 anymore
    if strings.Contains(src, "Select1(recvCase") {{
        fmt.Println("FAIL: Receive still uses old Select1 pattern")
        os.Exit(1)
    }}

    // Should NOT create recvCase
    if strings.Contains(src, "NewRecvCase") {{
        fmt.Println("FAIL: Receive still creates recvCase")
        os.Exit(1)
    }}

    fmt.Println("PASS: Receive method refactored correctly")
}}
""",
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_unbuffered_try_send_unified():
    """TrySend unifies buffered and unbuffered channel handling with switch on state."""
    r = subprocess.run(
        ["go", "run", "-"],
        input=f"""package main
import (
    "fmt"
    "os"
    "strings"
)

func main() {{
    content, err := os.ReadFile("{CHANNEL_FILE}")
    if err != nil {{
        fmt.Println("FAIL: Cannot read channel.go:", err)
        os.Exit(1)
    }}
    src := string(content)

    // TrySend should use switch on c.state
    if !strings.Contains(src, "switch c.state {{") {{
        fmt.Println("FAIL: TrySend does not use switch on state")
        os.Exit(1)
    }}

    // Should handle Buffered case in TrySend
    if !strings.Contains(src, "case Buffered:") {{
        fmt.Println("FAIL: TrySend does not handle Buffered case")
        os.Exit(1)
    }}

    // Should NOT call separate BufferedTrySend or UnbufferedTrySend helpers
    if strings.Contains(src, "BufferedTrySend") || strings.Contains(src, "UnbufferedTrySend") {{
        fmt.Println("FAIL: TrySend still calls old helper methods")
        os.Exit(1)
    }}

    fmt.Println("PASS: TrySend unified correctly")
}}
""",
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_unbuffered_try_receive_unified():
    """TryReceive unifies buffered and unbuffered channel handling with switch on state."""
    r = subprocess.run(
        ["go", "run", "-"],
        input=f"""package main
import (
    "fmt"
    "os"
    "strings"
)

func main() {{
    content, err := os.ReadFile("{CHANNEL_FILE}")
    if err != nil {{
        fmt.Println("FAIL: Cannot read channel.go:", err)
        os.Exit(1)
    }}
    src := string(content)

    // TryReceive should use switch on c.state
    switchCount := strings.Count(src, "switch c.state {{")
    if switchCount < 2 {{
        // TrySend and TryReceive both need switch statements
        fmt.Println("FAIL: Not enough switch statements on state (need at least 2)")
        os.Exit(1)
    }}

    // Should handle SndWait case in TryReceive (receiving from waiting sender)
    if !strings.Contains(src, "case SndWait:") {{
        fmt.Println("FAIL: TryReceive does not handle SndWait case")
        os.Exit(1)
    }}

    // Should NOT call separate helper methods
    if strings.Contains(src, "BufferedTryReceive") || strings.Contains(src, "UnbufferedTryReceive") {{
        fmt.Println("FAIL: TryReceive still calls old helper methods")
        os.Exit(1)
    }}

    fmt.Println("PASS: TryReceive unified correctly")
}}
""",
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_helper_methods_removed():
    """Helper methods (BufferedTrySend, BufferedTryReceive, UnbufferedTrySend, UnbufferedTryReceive) removed."""
    r = subprocess.run(
        ["go", "run", "-"],
        input=f"""package main
import (
    "fmt"
    "os"
    "strings"
)

func main() {{
    content, err := os.ReadFile("{CHANNEL_FILE}")
    if err != nil {{
        fmt.Println("FAIL: Cannot read channel.go:", err)
        os.Exit(1)
    }}
    src := string(content)

    // Old helper methods should NOT exist
    helpers := []string{{"func (c *Channel[T]) BufferedTrySend",
        "func (c *Channel[T]) BufferedTryReceive",
        "func (c *Channel[T]) UnbufferedTrySend",
        "func (c *Channel[T]) UnbufferedTryReceive"}}

    for _, helper := range helpers {{
        if strings.Contains(src, helper) {{
            fmt.Println("FAIL: Old helper method still exists:", helper)
            os.Exit(1)
        }}
    }}

    fmt.Println("PASS: Helper methods removed")
}}
""",
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_state_field_not_pointer():
    """Channel v field changed from pointer (*T) to value (T) type."""
    r = subprocess.run(
        ["go", "run", "-"],
        input=f"""package main
import (
    "fmt"
    "os"
    "strings"
)

func main() {{
    content, err := os.ReadFile("{CHANNEL_FILE}")
    if err != nil {{
        fmt.Println("FAIL: Cannot read channel.go:", err)
        os.Exit(1)
    }}
    src := string(content)

    // Find the Channel struct definition - look for the struct block
    structStart := strings.Index(src, "type Channel[T any] struct {{")
    if structStart == -1 {{
        fmt.Println("FAIL: Could not find Channel struct definition")
        os.Exit(1)
    }}

    // Find the closing brace of the struct
    structEnd := strings.Index(src[structStart:], "\n}}")
    if structEnd == -1 {{
        // Try finding single closing brace
        structEnd = strings.Index(src[structStart:], "}}")
    }}
    if structEnd == -1 {{
        fmt.Println("FAIL: Could not find end of Channel struct")
        os.Exit(1)
    }}
    structEnd += structStart

    // Extract struct body
    structBody := src[structStart:structEnd]

    // In the struct, v should be value type, not pointer
    // The old was: v *T
    // The new is: v T
    if strings.Contains(structBody, "v *T") {{
        fmt.Println("FAIL: Channel v field is still pointer (*T)")
        os.Exit(1)
    }}

    if !strings.Contains(structBody, "v T") {{
        fmt.Println("FAIL: Channel v field should be value type (v T)")
        os.Exit(1)
    }}

    fmt.Println("PASS: Channel v field is value type")
}}
""",
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

def test_go_model_tests_pass():
    """Go model tests still pass after channel refactor."""
    # First check that the code compiles
    r = _check_go_build()
    assert r.returncode == 0, f"Go build failed: {r.stderr}"

    # Run Go tests for the channel package if they exist
    r = subprocess.run(
        ["go", "test", "./model/channel/", "-v", "-timeout", "60s"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Tests may not exist, which is OK - we just need the code to compile
    # If tests exist, they should pass
    if r.returncode != 0:
        # If there are no tests, that's fine - the build succeeded
        if "no test files" in r.stderr or "no test files" in r.stdout:
            return
        # If tests fail, that's an issue
        assert False, f"Go tests failed: {r.stderr}\n{r.stdout}"
