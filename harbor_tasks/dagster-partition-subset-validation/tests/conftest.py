import pathlib


def pytest_sessionfinish(session, exitstatus):
    """Write reward.txt based on test results."""
    reward = 1.0 if exitstatus == 0 else 0.0
    pathlib.Path("/logs/verifier/reward.txt").write_text(str(reward))
