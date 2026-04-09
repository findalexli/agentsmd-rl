"""Pytest configuration to write reward file after test run."""

import os


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Write reward file based on test outcomes.

    This runs after all tests complete and writes 1 if all tests passed,
    0 if any tests failed.
    """
    os.makedirs("/logs/verifier", exist_ok=True)
    # exitstatus 0 means all tests passed
    reward = 1 if exitstatus == 0 else 0
    with open("/logs/verifier/reward.txt", "w") as f:
        f.write(str(reward))
