# pytest hook to write reward file
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    try:
        failed = len(terminalreporter.stats.get('failed', []))
        passed = len(terminalreporter.stats.get('passed', []))
        total = failed + passed
        reward = 1 if failed == 0 else 0
        with open("/logs/verifier/reward.txt", "w") as f:
            f.write(str(reward))
        print(f"\n[WROTE] reward={reward} ({total-failed}/{total} passed)")
    except Exception as e:
        print(f"\n[WARN] could not write reward: {e}")