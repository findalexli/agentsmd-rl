"""Behavioral checks for jollyday-agents-md-and-split-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jollyday")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-holiday-calendar-xml/SKILL.md')
    assert 'xsi:schemaLocation="https://focus_shift.de/jollyday/schema/holiday https://focus_shift.de/jollyday/schema/holiday/holiday.xsd">' in text, "expected to find: " + 'xsi:schemaLocation="https://focus_shift.de/jollyday/schema/holiday https://focus_shift.de/jollyday/schema/holiday/holiday.xsd">'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-holiday-calendar-xml/SKILL.md')
    assert '`JANUARY`, `FEBRUARY`, `MARCH`, `APRIL`, `MAY`, `JUNE`, `JULY`, `AUGUST`, `SEPTEMBER`, `OCTOBER`, `NOVEMBER`, `DECEMBER`' in text, "expected to find: " + '`JANUARY`, `FEBRUARY`, `MARCH`, `APRIL`, `MAY`, `JUNE`, `JULY`, `AUGUST`, `SEPTEMBER`, `OCTOBER`, `NOVEMBER`, `DECEMBER`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-holiday-calendar-xml/SKILL.md')
    assert '<FixedWeekday which="THIRD" weekday="MONDAY" month="JANUARY" descriptionPropertiesKey="MARTIN_LUTHER_KING"/>' in text, "expected to find: " + '<FixedWeekday which="THIRD" weekday="MONDAY" month="JANUARY" descriptionPropertiesKey="MARTIN_LUTHER_KING"/>'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-holiday-description-properties/SKILL.md')
    assert 'Add entries to `jollyday-core/src/main/resources/descriptions/holiday_descriptions.properties`:' in text, "expected to find: " + 'Add entries to `jollyday-core/src/main/resources/descriptions/holiday_descriptions.properties`:'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-holiday-description-properties/SKILL.md')
    assert 'Add entries to `jollyday-core/src/main/resources/descriptions/country_descriptions.properties`:' in text, "expected to find: " + 'Add entries to `jollyday-core/src/main/resources/descriptions/country_descriptions.properties`:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-holiday-description-properties/SKILL.md')
    assert 'This guide explains how to add holiday descriptions to the properties files in Jollyday.' in text, "expected to find: " + 'This guide explains how to add holiday descriptions to the properties files in Jollyday.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-subdivision/SKILL.md')
    assert 'Subdivisions allow you to define holidays that are specific to certain regions within a country. For example, in Germany, Bavaria (BY) has different holidays than Berlin (BE).' in text, "expected to find: " + 'Subdivisions allow you to define holidays that are specific to certain regions within a country. For example, in Germany, Bavaria (BY) has different holidays than Berlin (BE).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-subdivision/SKILL.md')
    assert 'This guide explains how to add regional holiday configurations for subdivisions (states, provinces, regions) based on ISO 3166-2 codes.' in text, "expected to find: " + 'This guide explains how to add regional holiday configurations for subdivisions (states, provinces, regions) based on ISO 3166-2 codes.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-subdivision/SKILL.md')
    assert '- **Nested subdivisions**: For cities within states, include both codes (e.g., `inSubdivision("by", "mu")` for Munich in Bavaria)' in text, "expected to find: " + '- **Nested subdivisions**: For cities within states, include both codes (e.g., `inSubdivision("by", "mu")` for Munich in Bavaria)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/how-to-add-a-new-holiday-calendar-for-a-country/SKILL.md')
    assert '.agents/skills/how-to-add-a-new-holiday-calendar-for-a-country/SKILL.md' in text, "expected to find: " + '.agents/skills/how-to-add-a-new-holiday-calendar-for-a-country/SKILL.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/register-holiday-calendar/SKILL.md')
    assert 'ANTARCTICA("AQ"), ALBANIA("AL"), ANDORRA("AD"), ARGENTINA("AR"), ARMENIA("AM"), AUSTRALIA("AU"), AUSTRIA("AT"),' in text, "expected to find: " + 'ANTARCTICA("AQ"), ALBANIA("AL"), ANDORRA("AD"), ARGENTINA("AR"), ARMENIA("AM"), AUSTRALIA("AU"), AUSTRIA("AT"),'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/register-holiday-calendar/SKILL.md')
    assert 'BAHAMAS("BS"), BELARUS("BY"), BELGIUM("BE"), BERMUDA("BM"), BOLIVIA("BO"), BRAZIL("BR"), ...' in text, "expected to find: " + 'BAHAMAS("BS"), BELARUS("BY"), BELGIUM("BE"), BERMUDA("BM"), BOLIVIA("BO"), BRAZIL("BR"), ...'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/register-holiday-calendar/SKILL.md')
    assert 'This guide explains how to register a new country calendar in the `HolidayCalendar` enum.' in text, "expected to find: " + 'This guide explains how to register a new country calendar in the `HolidayCalendar` enum.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/write-holiday-tests/SKILL.md')
    assert '.hasFixedWeekdayHoliday("LABOUR_DAY", java.time.DayOfWeek.MONDAY, SEPTEMBER, java.time.temporal.TemporalAdjusters.firstInMonth(java.time.DayOfWeek.MONDAY))' in text, "expected to find: " + '.hasFixedWeekdayHoliday("LABOUR_DAY", java.time.DayOfWeek.MONDAY, SEPTEMBER, java.time.temporal.TemporalAdjusters.firstInMonth(java.time.DayOfWeek.MONDAY))'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/write-holiday-tests/SKILL.md')
    assert 'This guide explains how to write tests for new or modified holiday calendars using the `CalendarCheckerApi`.' in text, "expected to find: " + 'This guide explains how to write tests for new or modified holiday calendars using the `CalendarCheckerApi`.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/write-holiday-tests/SKILL.md')
    assert 'Create test file at: `jollyday-tests/src/test/java/de/focus_shift/jollyday/tests/[CountryName]Test.java`' in text, "expected to find: " + 'Create test file at: `jollyday-tests/src/test/java/de/focus_shift/jollyday/tests/[CountryName]Test.java`'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '**Jollyday** is a Java library to query public holidays. It currently supports **over 110 countries**. The holiday data is stored in XML files (one for each country) and will be read from the classpat' in text, "expected to find: " + '**Jollyday** is a Java library to query public holidays. It currently supports **over 110 countries**. The holiday data is stored in XML files (one for each country) and will be read from the classpat'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert 'parser.impl.de.focus_shift.jollyday.core.spi.ChristianHolidayConfiguration = de.focus_shift.jollyday.core.parser.impl.ChristianHolidayParser' in text, "expected to find: " + 'parser.impl.de.focus_shift.jollyday.core.spi.ChristianHolidayConfiguration = de.focus_shift.jollyday.core.parser.impl.ChristianHolidayParser'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert 'parser.impl.de.focus_shift.jollyday.core.spi.IslamicHolidayConfiguration = de.focus_shift.jollyday.core.parser.impl.IslamicHolidayParser' in text, "expected to find: " + 'parser.impl.de.focus_shift.jollyday.core.spi.IslamicHolidayConfiguration = de.focus_shift.jollyday.core.parser.impl.IslamicHolidayParser'[:80]

