#!/usr/bin/env bash
set -euo pipefail

cd /workspace/exchange-calendars

# Idempotency guard
if grep -qF "Expected sessions and times for each calendar are stored in a .csv file in @test" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -31,7 +31,90 @@ See @pyproject.toml for project metadata and dependencies.
 ### Repository Layout
 
 ```
-TODO
+exchange_calendars_fork/
+├── .agents/                                # instructions for LLM coding agents
+│   └── skills/                             # skills for LLM coding agents
+│       ├── dependencies-management/
+│       │   └── SKILL.md
+│       └── update-agents-md/
+│           └── SKILL.md
+├── .devcontainer/
+│   ├── library-scripts/
+│   │   ├── common-debian.sh
+│   │   ├── node-debian.sh
+│   │   └── python-debian.sh
+│   ├── base.Dockerfile
+│   ├── devcontainer.json
+│   └── Dockerfile
+├── .github/
+│   ├── workflows/
+│   │   ├── benchmark.yml
+│   │   ├── labeler.yml
+│   │   ├── main.yml                        # build and run full test suite
+│   │   ├── master-merge.yml
+│   │   ├── release.yml
+│   │   └── update_deps.yml
+│   ├── dependabot.yml
+│   ├── pull_request_template.md
+│   └── release-drafter-config.yml
+├── docs/
+│   ├── dev/
+│   │   └── depenencies_update.md
+│   ├── tutorials/
+│   │   ├── calendar_methods.ipynb
+│   │   ├── calendar_properties.ipynb
+│   │   ├── minutes.ipynb
+│   │   ├── sessions.ipynb
+│   │   └── trading_index.ipynb
+│   └── changes_archive.md
+├── etc/                                    # developer scripts and reference materials
+│   ├── ecal/                               # show holiday calendar in the terminal
+│   ├── lunisolar/
+│   ├── NYSE-Historical-Closings.pdf
+│   ├── bench.py
+│   ├── check_holidays.py
+│   ├── factory_bounds.py                   # explore bounds of a calendar factory
+│   ├── make_exchange_calendar_test_csv.py  # create a answers .csv file for a calendar
+│   └── update_xkrx_holidays.py
+├── exchange_calendars/
+│   ├── pandas_extensions/
+│   │   ├── holiday.py
+│   │   ├── korean_holiday.py
+│   │   └── offsets.py
+│   ├── utils/
+│   │   └── pandas_utils.py
+│   ├── always_open.py
+│   ├── calendar_helpers.py
+│   ├── calendar_utils.py                    # calendar registry and dispatch
+│   ├── common_holidays.py
+│   ├── ecal.py                              # show holiday calendar in the terminal
+│   ├── errors.py
+│   ├── exchange_calendar.py                 # includes base ExchangeCalendar class
+│   ├── exchange_calendar_<code>.py          # calendars for each exchange
+│   ├── lunisolar_holidays.py
+│   ├── precomputed_exchange_calendar.py
+│   ├── tase_holidays.py
+│   ├── us_futures_calendar.py
+│   ├── us_holidays.py
+│   ├── weekday_calendar.py
+│   ├── xbkk_holidays.py
+│   ├── xkls_holidays.py
+│   ├── xkrx_holidays.py
+│   └── xtks_holidays.py
+├── tests/
+│   ├── resources/                           # .csv answer files for each calendar
+│   └── test_<code>_calendar.py              # test file for each calendar
+├── .pre-commit-config.yaml
+├── .python-version
+├── AGENTS.md
+├── CLAUDE.md
+├── LICENSE
+├── MANIFEST.in
+├── pyproject.toml
+├── README.md
+├── requirements.txt
+├── ruff.toml
+└── uv.lock
 ```
 
 ## Technology Stack
@@ -64,12 +147,11 @@ pre-commit install
 
 ### Testing
 
-Each calendar has a dedicated test file containing a dedicated test suite defined on a subclass of the common base class `ExchangeCalendarTestBase` (in @tests\test_exchange_calendar.py).
-- tests are in @tests/
-- doctests are included to some methods/functions
-- test with `pytest`
+- tests are in @tests/.
+- doctests are included to some methods/functions.
+- test with `pytest`.
 - see @pytest.ini for configuration; options are applied automatically via `addopts`.
-- shared fixtures are in @tests/conftest.py
+- shared fixtures are in @tests/conftest.py.
 
 Commands to run tests:
 ```bash
@@ -86,6 +168,11 @@ pytest tests/test_module.py::test_name
 pytest -v
 ```
 
+#### Testing Architecture
+Each calendar has a dedicated test file containing a dedicated test suite defined on a subclass of the common base class `ExchangeCalendarTestBase` (in @tests\test_exchange_calendar.py).
+
+Expected sessions and times for each calendar are stored in a .csv file in @tests\resources. During testing the contents of a .csv file are stored by an instance of the `Answers` class (of @tests\test_exchange_calendar.py). Tests then call the methods of the `Answers` class to access expected values.
+
 ### Pre-commit Hooks
 
 See @.pre-commit-config.yaml for pre-commit implementation.
PATCH

echo "Gold patch applied."
