# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import pytest
from sqlalchemy.orm.session import Session

from superset.daos.report import ReportScheduleDAO
from superset.reports.models import ReportSchedule, ReportScheduleType


@pytest.fixture(autouse=True)
def _create_tables(session: Session) -> None:
    ReportSchedule.metadata.create_all(session.get_bind())  # pylint: disable=no-member


def _make(session: Session, name: str, extra_json: str) -> ReportSchedule:
    report = ReportSchedule(
        name=name,
        type=ReportScheduleType.REPORT,
        crontab="0 9 * * *",
        extra_json=extra_json,
    )
    session.add(report)
    session.flush()
    return report


def test_percent_in_slug_must_be_literal(session: Session) -> None:
    """Slug containing '%' must not match arbitrary characters via wildcard."""
    _make(session, "literal-percent", '{"slug": "abc%xyz"}')
    _make(session, "no-percent", '{"slug": "abcZZxyz"}')

    results = ReportScheduleDAO.find_by_extra_metadata("abc%xyz")

    names = sorted(r.name for r in results)
    assert names == ["literal-percent"], f"unexpected matches: {names}"


def test_underscore_in_slug_must_be_literal(session: Session) -> None:
    """Slug containing '_' must not match a single arbitrary character."""
    _make(session, "literal-underscore", '{"id": "p_q"}')
    _make(session, "single-char", '{"id": "pXq"}')

    results = ReportScheduleDAO.find_by_extra_metadata("p_q")

    names = sorted(r.name for r in results)
    assert names == ["literal-underscore"], f"unexpected matches: {names}"


def test_trailing_percent_no_wildcard(session: Session) -> None:
    """Slug 'foo%' must not match 'foobar' — '%' stays literal."""
    _make(session, "exact-foo-percent", '{"v": "foo%"}')
    _make(session, "broader", '{"v": "foobar"}')

    results = ReportScheduleDAO.find_by_extra_metadata("foo%")

    names = sorted(r.name for r in results)
    assert names == ["exact-foo-percent"], f"unexpected matches: {names}"


def test_basic_substring_match_still_works(session: Session) -> None:
    """A normal slug (no special chars) still finds its row."""
    _make(session, "match-me", '{"slug": "PLAIN-id-1234"}')
    _make(session, "no-match", '{"slug": "OTHER"}')

    results = ReportScheduleDAO.find_by_extra_metadata("PLAIN-id-1234")

    names = sorted(r.name for r in results)
    assert names == ["match-me"], f"unexpected matches: {names}"


def test_no_match_returns_empty_list(session: Session) -> None:
    """Slug not present anywhere returns []."""
    _make(session, "report1", '{"slug": "alpha"}')

    results = ReportScheduleDAO.find_by_extra_metadata("zeta")

    assert results == []
