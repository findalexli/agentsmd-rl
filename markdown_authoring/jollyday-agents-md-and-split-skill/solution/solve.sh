#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jollyday

# Idempotency guard
if grep -qF "xsi:schemaLocation=\"https://focus_shift.de/jollyday/schema/holiday https://focus" ".agents/skills/add-holiday-calendar-xml/SKILL.md" && grep -qF "Add entries to `jollyday-core/src/main/resources/descriptions/holiday_descriptio" ".agents/skills/add-holiday-description-properties/SKILL.md" && grep -qF "Subdivisions allow you to define holidays that are specific to certain regions w" ".agents/skills/add-subdivision/SKILL.md" && grep -qF ".agents/skills/how-to-add-a-new-holiday-calendar-for-a-country/SKILL.md" ".agents/skills/how-to-add-a-new-holiday-calendar-for-a-country/SKILL.md" && grep -qF "ANTARCTICA(\"AQ\"), ALBANIA(\"AL\"), ANDORRA(\"AD\"), ARGENTINA(\"AR\"), ARMENIA(\"AM\"), " ".agents/skills/register-holiday-calendar/SKILL.md" && grep -qF ".hasFixedWeekdayHoliday(\"LABOUR_DAY\", java.time.DayOfWeek.MONDAY, SEPTEMBER, jav" ".agents/skills/write-holiday-tests/SKILL.md" && grep -qF "**Jollyday** is a Java library to query public holidays. It currently supports *" "agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/add-holiday-calendar-xml/SKILL.md b/.agents/skills/add-holiday-calendar-xml/SKILL.md
@@ -0,0 +1,222 @@
+---
+name: add-holiday-calendar-xml
+description: Create XML holiday calendar configuration files for a new country or region
+---
+
+# How to Add Holiday Calendar XML
+
+This guide explains how to create XML holiday calendar files for countries in Jollyday.
+
+## File Location
+
+Create a new file at: `jollyday-core/src/main/resources/holidays/Holidays_[country_code].xml`
+
+## Root Structure
+
+```xml
+<?xml version="1.0" encoding="UTF-8"?>
+
+<Configuration hierarchy="[country_code]" description="[Country Name]"
+               xmlns="https://focus_shift.de/jollyday/schema/holiday"
+               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
+               xsi:schemaLocation="https://focus_shift.de/jollyday/schema/holiday https://focus_shift.de/jollyday/schema/holiday/holiday.xsd">
+  <Holidays>
+    <!-- Add your holidays here -->
+  </Holidays>
+
+  <Sources>
+    <Source>https://en.wikipedia.org/wiki/Public_holidays_in_[Country]</Source>
+    <Source of="ISO 3166">https://www.iso.org/obp/ui/#iso:code:3166:[country_code]</Source>
+    <Source of="ISO 3166-2">https://en.wikipedia.org/wiki/ISO_3166-2:[country_code]</Source>
+  </Sources>
+</Configuration>
+```
+
+### Root Element Attributes
+
+| Attribute     | Description                                              |
+|---------------|----------------------------------------------------------|
+| `hierarchy`   | ISO 3166-1 alpha-2 country code (e.g., "de", "us", "fr") |
+| `description` | Full country name in English                             |
+
+## Holiday Types
+
+### Fixed Date Holidays
+
+For holidays on a fixed calendar date:
+
+```xml
+<Fixed month="JANUARY" day="1" descriptionPropertiesKey="NEW_YEAR"/>
+```
+
+With validity period:
+
+```xml
+<Fixed month="OCTOBER" day="31" validFrom="2017" descriptionPropertiesKey="REFORMATION_DAY"/>
+<Fixed month="JUNE" day="19" validFrom="2021" descriptionPropertiesKey="JUNETEENTH"/>
+```
+
+### Fixed Weekday Holidays
+
+For holidays on a specific weekday occurrence in a month:
+
+```xml
+<FixedWeekday which="FIRST" weekday="MONDAY" month="SEPTEMBER" descriptionPropertiesKey="LABOUR_DAY"/>
+<FixedWeekday which="THIRD" weekday="MONDAY" month="JANUARY" descriptionPropertiesKey="MARTIN_LUTHER_KING"/>
+<FixedWeekday which="FOURTH" weekday="THURSDAY" month="NOVEMBER" descriptionPropertiesKey="THANKSGIVING"/>
+<FixedWeekday which="LAST" weekday="MONDAY" month="MAY" descriptionPropertiesKey="MEMORIAL_DAY"/>
+```
+
+**`which` values**: `FIRST`, `SECOND`, `THIRD`, `FOURTH`, `LAST`
+
+### Christian (Easter-based) Holidays
+
+For Christian holidays that depend on Easter:
+
+```xml
+<ChristianHoliday type="GOOD_FRIDAY"/>
+<ChristianHoliday type="EASTER_MONDAY"/>
+<ChristianHoliday type="ASCENSION_DAY"/>
+<ChristianHoliday type="WHIT_MONDAY"/>
+<ChristianHoliday type="CORPUS_CHRISTI"/>
+<ChristianHoliday type="PENTECOST"/>
+```
+
+With optional `localizedType`:
+
+```xml
+<ChristianHoliday type="GOOD_FRIDAY" localizedType="OBSERVANCE"/>
+```
+
+### Islamic Calendar Holidays
+
+For Islamic calendar-based holidays:
+
+```xml
+<IslamicHoliday type="ID_AL_FITR"/>
+<IslamicHoliday type="ID_AL_FITR_2"/>
+<IslamicHoliday type="ID_AL_FITR_3"/>
+<IslamicHoliday type="ID_UL_ADHA"/>
+<IslamicHoliday type="ARAFAAT"/>
+<IslamicHoliday type="NEWYEAR"/>
+<IslamicHoliday type="MAWLID_AN_NABI"/>
+```
+
+### Relative to Fixed Date
+
+For holidays calculated relative to a fixed date:
+
+```xml
+<RelativeToFixed validFrom="1990" descriptionPropertiesKey="REPENTANCE_PRAYER">
+  <Weekday>WEDNESDAY</Weekday>
+  <When>BEFORE</When>
+  <Date month="NOVEMBER" day="23"/>
+</RelativeToFixed>
+```
+
+**`When` values**: `BEFORE`, `AFTER`
+
+### Moving Conditions
+
+For holidays that shift to weekdays when falling on weekends:
+
+```xml
+<Fixed month="JANUARY" day="1" descriptionPropertiesKey="NEW_YEAR">
+  <MovingCondition substitute="SATURDAY" with="PREVIOUS" weekday="FRIDAY"/>
+  <MovingCondition substitute="SUNDAY" with="NEXT" weekday="MONDAY"/>
+</Fixed>
+```
+
+## Regional/Subdivision Holidays
+
+For countries with regional holidays (states, provinces):
+
+```xml
+<SubConfigurations hierarchy="[region_code]" description="[Region Name]">
+  <Holidays>
+    <Fixed month="MARCH" day="8" descriptionPropertiesKey="INTERNATIONAL_WOMAN"/>
+  </Holidays>
+</SubConfigurations>
+```
+
+Example with nested subdivisions:
+
+```xml
+<SubConfigurations hierarchy="by" description="Bavaria">
+  <Holidays>
+    <Fixed month="JANUARY" day="6" descriptionPropertiesKey="EPIPHANY"/>
+  </Holidays>
+
+  <SubConfigurations hierarchy="mu" description="Munich">
+    <Holidays>
+      <Fixed day="15" month="AUGUST" descriptionPropertiesKey="ASSUMPTION_DAY"/>
+    </Holidays>
+  </SubConfigurations>
+</SubConfigurations>
+```
+
+## Common Attributes Reference
+
+| Attribute                  | Description                | Example                  |
+|----------------------------|----------------------------|--------------------------|
+| `month`                    | Month (English, uppercase) | `JANUARY`, `DECEMBER`    |
+| `day`                      | Day of month               | `1`, `25`                |
+| `weekday`                  | Day of week                | `MONDAY`, `FRIDAY`       |
+| `which`                    | Which occurrence           | `FIRST`, `LAST`, `THIRD` |
+| `validFrom`                | Start year                 | `1990`, `2021`           |
+| `validTo`                  | End year                   | `1990`, `2020`           |
+| `descriptionPropertiesKey` | Key for description        | `NEW_YEAR`               |
+| `localizedType`            | Holiday type variant       | `OBSERVANCE`             |
+
+## Available Values
+
+### Months
+`JANUARY`, `FEBRUARY`, `MARCH`, `APRIL`, `MAY`, `JUNE`, `JULY`, `AUGUST`, `SEPTEMBER`, `OCTOBER`, `NOVEMBER`, `DECEMBER`
+
+### Weekdays
+`MONDAY`, `TUESDAY`, `WEDNESDAY`, `THURSDAY`, `FRIDAY`, `SATURDAY`, `SUNDAY`
+
+### ChristianHoliday Types
+- `GOOD_FRIDAY`, `EASTER`, `EASTER_MONDAY`, `EASTER_SATURDAY`, `EASTER_TUESDAY`
+- `ASCENSION_DAY`, `WHIT_MONDAY`, `PENTECOST`, `PENTECOST_MONDAY`
+- `CORPUS_CHRISTI`, `CARNIVAL`, `MARDI_GRAS`, `MAUNDY_THURSDAY`, `ASH_WEDNESDAY`
+
+### IslamicHoliday Types
+- `NEWYEAR`, `MAWLID_AN_NABI`, `LAILAT_AL_BARAT`, `LAILAT_AL_MIRAJ`, `LAILAT_AL_QADR`
+- `ASCHURA`, `RAMADAN`, `RAMADAN_END`
+- `ID_AL_FITR`, `ID_AL_FITR_2`, `ID_AL_FITR_3`
+- `ARAFAAT`, `ID_UL_ADHA`, `ID_UL_ADHA_2`, `ID_UL_ADHA_3`
+
+## Complete Example: Germany (Simplified)
+
+```xml
+<?xml version="1.0" encoding="UTF-8"?>
+
+<Configuration hierarchy="de" description="Germany"
+               xmlns="https://focus_shift.de/jollyday/schema/holiday"
+               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
+               xsi:schemaLocation="https://focus_shift.de/jollyday/schema/holiday https://focus_shift.de/jollyday/schema/holiday/holiday.xsd">
+  <Holidays>
+    <Fixed month="JANUARY" day="1" descriptionPropertiesKey="NEW_YEAR"/>
+    <Fixed month="MAY" day="1" descriptionPropertiesKey="LABOUR_DAY"/>
+    <Fixed month="DECEMBER" day="25" descriptionPropertiesKey="FIRST_CHRISTMAS_DAY"/>
+    <Fixed month="DECEMBER" day="26" descriptionPropertiesKey="SECOND_CHRISTMAS_DAY"/>
+    <ChristianHoliday type="GOOD_FRIDAY"/>
+    <ChristianHoliday type="EASTER_MONDAY"/>
+    <ChristianHoliday type="ASCENSION_DAY"/>
+    <ChristianHoliday type="WHIT_MONDAY"/>
+  </Holidays>
+
+  <Sources>
+    <Source>https://en.wikipedia.org/wiki/Public_holidays_in_Germany</Source>
+    <Source of="ISO 3166">https://www.iso.org/obp/ui/#iso:code:3166:DE</Source>
+    <Source of="ISO 3166-2">https://en.wikipedia.org/wiki/ISO_3166-2:DE</Source>
+  </Sources>
+</Configuration>
+```
+
+## References
+
+- **Schema XSD**: `jollyday-core/src/main/resources/focus_shift.de/jollyday/schema/holiday/holiday.xsd`
+- **Online Schema**: `https://focus_shift.de/jollyday/schema/holiday/holiday.xsd`
+- **Examples**: Review existing `Holidays_*.xml` files in `jollyday-core/src/main/resources/holidays/`
diff --git a/.agents/skills/add-holiday-description-properties/SKILL.md b/.agents/skills/add-holiday-description-properties/SKILL.md
@@ -0,0 +1,146 @@
+---
+name: add-holiday-description-properties
+description: Add holiday and country description properties for localization
+---
+
+# How to Add Holiday Description Properties
+
+This guide explains how to add holiday descriptions to the properties files in Jollyday.
+
+## Holiday Descriptions
+
+### Base English Descriptions
+
+Add entries to `jollyday-core/src/main/resources/descriptions/holiday_descriptions.properties`:
+
+```properties
+holiday.description.NEW_YEAR                    = New Year's Day
+holiday.description.LABOUR_DAY                  = Labour Day
+holiday.description.CHRISTMAS                   = Christmas
+holiday.description.INDEPENDENCE_DAY            = Independence Day
+holiday.description.NATIONAL_DAY                = National Day
+holiday.description.GOOD_FRIDAY                 = Good Friday
+holiday.description.EASTER_MONDAY               = Easter Monday
+holiday.description.FIRST_CHRISTMAS_DAY         = First Day of Christmas
+holiday.description.SECOND_CHRISTMAS_DAY        = Second Day of Christmas
+```
+
+### Key Naming Conventions
+
+- Use **UPPERCASE** with underscores: `NEW_YEAR`, `LABOUR_DAY`, `GOOD_FRIDAY`
+- For multi-word holidays: `FIRST_CHRISTMAS_DAY`, `SECOND_CHRISTMAS_DAY`
+- Country-specific: `REFORMATION_DAY`, `UNIFICATION_GERMANY`, `MARTIN_LUTHER_KING`
+- Always prefix with `holiday.description.`
+
+### Localized Descriptions
+
+Add entries to locale-specific files:
+
+| File                                 | Language   |
+|--------------------------------------|------------|
+| `holiday_descriptions_de.properties` | German     |
+| `holiday_descriptions_el.properties` | Greek      |
+| `holiday_descriptions_fr.properties` | French     |
+| `holiday_descriptions_nl.properties` | Dutch      |
+| `holiday_descriptions_pt.properties` | Portuguese |
+| `holiday_descriptions_sv.properties` | Swedish    |
+
+**Example - German:**
+
+```properties
+holiday.description.NEW_YEAR            = Neujahr
+holiday.description.LABOUR_DAY          = Tag der Arbeit
+holiday.description.CHRISTMAS           = 1. Weihnachtstag
+holiday.description.GOOD_FRIDAY         = Karfreitag
+holiday.description.EASTER_MONDAY       = Ostermontag
+```
+
+## Country Descriptions
+
+### Base English Country Descriptions
+
+Add entries to `jollyday-core/src/main/resources/descriptions/country_descriptions.properties`:
+
+```properties
+country.description.de = Germany
+country.description.us = United States
+country.description.fr = France
+```
+
+### Localized Country Descriptions
+
+Add entries to locale-specific files:
+
+```properties
+# country_descriptions_de.properties
+country.description.de = Deutschland
+country.description.us = Vereinigte Staaten
+country.description.fr = Frankreich
+```
+
+## Property File Locations
+
+| File                                                    | Purpose                 |
+|---------------------------------------------------------|-------------------------|
+| `descriptions/holiday_descriptions.properties`          | English holiday names   |
+| `descriptions/holiday_descriptions_[locale].properties` | Localized holiday names |
+| `descriptions/country_descriptions.properties`          | English country names   |
+| `descriptions/country_descriptions_[locale].properties` | Localized country names |
+
+## Complete Example
+
+For adding a new holiday key `REFORMATION_DAY`:
+
+**1. Base properties:**
+```properties
+# holiday_descriptions.properties
+holiday.description.REFORMATION_DAY = Reformation Day
+
+# country_descriptions.properties
+country.description.xx = Your Country Name
+```
+
+**2. German localization:**
+```properties
+# holiday_descriptions_de.properties
+holiday.description.REFORMATION_DAY = Reformationsfest
+
+# country_descriptions_de.properties
+country.description.xx = Ihr Landname
+```
+
+**3. French localization:**
+```properties
+# holiday_descriptions_fr.properties
+holiday.description.REFORMATION_DAY = Jour de la Réformation
+
+# country_descriptions_fr.properties
+country.description.xx = Votre nom de pays
+```
+
+## Best Practices
+
+1. **Consistent naming**: Use the same key across all locale files
+2. **English first**: Always add the English description first
+3. **Localized when available**: Add translations for supported locales
+4. **No empty values**: Leave out the line entirely if translation unavailable
+5. **Follow existing patterns**: Review existing descriptions for style consistency
+
+## Common Holiday Keys
+
+| Key                          | Description             |
+|-------------------------------|---------------- --------|
+| `NEW_YEAR`                   | New Year's Day          |
+| `CHRISTMAS`                  | Christmas Day           |
+| `FIRST_CHRISTMAS_DAY`        | First Day of Christmas  |
+| `SECOND_CHRISTMAS_DAY`       | Second Day of Christmas |
+| `GOOD_FRIDAY`                | Good Friday             |
+| `EASTER_MONDAY`              | Easter Monday           |
+| `LABOUR_DAY`                 | Labour/May Day          |
+| `NATIONAL_DAY`               | National Day            |
+| `INDEPENDENCE_DAY`           | Independence Day        |
+| `ASCENSION_DAY`              | Ascension Day           |
+| `WHIT_MONDAY`                | Whit Monday/Pentecost   |
+| `CORPUS_CHRISTI`             | Corpus Christi          |
+| `EPIPHANY`                   | Epiphany/Bright Tuesday |
+| `REPELLENCE_PRAYER`          | Repentance Prayer       |
diff --git a/.agents/skills/add-subdivision/SKILL.md b/.agents/skills/add-subdivision/SKILL.md
@@ -0,0 +1,354 @@
+---
+name: add-subdivision
+description: Add regional/subdivision holiday configurations based on ISO 3166-2 codes
+---
+
+# How to Add Subdivisions
+
+This guide explains how to add regional holiday configurations for subdivisions (states, provinces, regions) based on ISO 3166-2 codes.
+
+## Overview
+
+Subdivisions allow you to define holidays that are specific to certain regions within a country. For example, in Germany, Bavaria (BY) has different holidays than Berlin (BE).
+
+## File Location
+
+Edit the country's XML file: `jollyday-core/src/main/resources/holidays/Holidays_[country_code].xml`
+
+## ISO 3166-2 Codes
+
+Subdivision codes follow the ISO 3166-2 standard:
+
+| Format  | Example | Meaning                    |
+|---------|---------|----------------------------|
+| `XX-YY` | `DE-BY` | Germany - Bavaria          |
+| `XXYY`  | `USCA`  | United States - California |
+
+The subdivision `hierarchy` attribute uses **only the regional part** (without the country prefix).
+
+## Basic Structure
+
+```xml
+<SubConfigurations hierarchy="[region_code]" description="[Region Name]">
+  <Holidays>
+    <!-- Regional-specific holidays go here -->
+  </Holidays>
+</SubConfigurations>
+```
+
+### Example - Germany (Baden-Württemberg)
+
+```xml
+<SubConfigurations hierarchy="bw" description="Baden-Württemberg">
+  <Holidays>
+    <Fixed month="JANUARY" day="6" descriptionPropertiesKey="EPIPHANY"/>
+    <Fixed month="NOVEMBER" day="1" descriptionPropertiesKey="ALL_SAINTS"/>
+    <ChristianHoliday type="CORPUS_CHRISTI"/>
+  </Holidays>
+</SubConfigurations>
+```
+
+## Adding a New Subdivision
+
+### Step 1: Find the ISO 3166-2 Code
+
+Look up the subdivision code:
+
+| Country       | Source                                      |
+|---------------|---------------------------------------------|
+| Germany       | https://en.wikipedia.org/wiki/ISO_3166-2:DE |
+| United States | https://en.wikipedia.org/wiki/ISO_3166-2:US |
+| France        | https://en.wikipedia.org/wiki/ISO_3166-2:FR |
+
+**Example - Germany codes:**
+
+| Code | Region                 |
+|------|------------------------|
+| `bw` | Baden-Württemberg      |
+| `by` | Bavaria                |
+| `be` | Berlin                 |
+| `bb` | Brandenburg            |
+| `he` | Hesse                  |
+| `nw` | North Rhine-Westphalia |
+
+### Step 2: Add SubConfigurations Element
+
+Insert the subdivision in your country's XML file:
+
+```xml
+<!-- Inside the root Configuration element, after <Holidays> and before closing </Configuration> -->
+
+<SubConfigurations hierarchy="xx" description="Your Region Name">
+  <Holidays>
+    <Fixed month="JANUARY" day="6" descriptionPropertiesKey="EPIPHANY"/>
+  </Holidays>
+</SubConfigurations>
+```
+
+### Step 3: Add Sources (Optional)
+
+Document the source of regional holiday information:
+
+```xml
+<SubConfigurations hierarchy="xx" description="Your Region Name">
+  <Holidays>
+    <Fixed month="JANUARY" day="6" descriptionPropertiesKey="EPIPHANY"/>
+  </Holidays>
+  <Sources>
+    <Source>https://www.region-official-website.gov/holidays</Source>
+  </Sources>
+</SubConfigurations>
+```
+
+## Nested Subdivisions
+
+Subdivisions can be nested for more granular regions (cities within states):
+
+```xml
+<SubConfigurations hierarchy="by" description="Bavaria">
+  <Holidays>
+    <Fixed month="JANUARY" day="6" descriptionPropertiesKey="EPIPHANY"/>
+  </Holidays>
+
+  <!-- Munich - city within Bavaria -->
+  <SubConfigurations hierarchy="mu" description="Munich">
+    <Holidays>
+      <Fixed month="AUGUST" day="15" descriptionPropertiesKey="ASSUMPTION_DAY"/>
+    </Holidays>
+  </SubConfigurations>
+
+  <!-- Augsburg - city within Bavaria -->
+  <SubConfigurations hierarchy="ag" description="Augsburg">
+    <Holidays>
+      <Fixed month="AUGUST" day="8" descriptionPropertiesKey="PEACE"/>
+      <Fixed month="AUGUST" day="15" descriptionPropertiesKey="ASSUMPTION_DAY"/>
+    </Holidays>
+  </SubConfigurations>
+</SubConfigurations>
+```
+
+## Complete Example - Germany
+
+```xml
+<?xml version="1.0" encoding="UTF-8"?>
+
+<Configuration hierarchy="de" description="Germany"
+       xmlns="https://focus_shift.de/jollyday/schema/holiday"
+       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
+       xsi:schemaLocation="https://focus_shift.de/jollyday/schema/holiday https://focus_shift.de/jollyday/schema/holiday/holiday.xsd">
+  <!-- National holidays apply to all Germany -->
+  <Holidays>
+    <Fixed month="JANUARY" day="1" descriptionPropertiesKey="NEW_YEAR"/>
+    <Fixed month="MAY" day="1" descriptionPropertiesKey="LABOUR_DAY"/>
+    <Fixed month="DECEMBER" day="25" descriptionPropertiesKey="FIRST_CHRISTMAS_DAY"/>
+    <Fixed month="DECEMBER" day="26" descriptionPropertiesKey="SECOND_CHRISTMAS_DAY"/>
+    <ChristianHoliday type="GOOD_FRIDAY"/>
+    <ChristianHoliday type="EASTER_MONDAY"/>
+    <ChristianHoliday type="ASCENSION_DAY"/>
+    <ChristianHoliday type="WHIT_MONDAY"/>
+  </Holidays>
+
+  <!-- Regional holidays for Bavaria only -->
+  <SubConfigurations hierarchy="by" description="Bavaria">
+    <Holidays>
+      <Fixed month="JANUARY" day="6" descriptionPropertiesKey="EPIPHANY"/>
+      <Fixed month="NOVEMBER" day="1" descriptionPropertiesKey="ALL_SAINTS"/>
+      <ChristianHoliday type="CORPUS_CHRISTI"/>
+    </Holidays>
+  </SubConfigurations>
+
+  <!-- Regional holidays for Berlin only -->
+  <SubConfigurations hierarchy="be" description="Berlin">
+    <Holidays>
+      <Fixed month="MARCH" day="8" descriptionPropertiesKey="INTERNATIONAL_WOMAN" validFrom="2019"/>
+    </Holidays>
+  </SubConfigurations>
+
+  <Sources>
+    <Source>https://en.wikipedia.org/wiki/Public_holidays_in_Germany</Source>
+    <Source of="ISO 3166-2">https://en.wikipedia.org/wiki/ISO_3166-2:DE</Source>
+  </Sources>
+</Configuration>
+```
+
+## Holiday Types in Subdivisions
+
+All holiday types can be used in subdivisions:
+
+```xml
+<SubConfigurations hierarchy="xx" description="Example Region">
+  <Holidays>
+    <!-- Fixed date -->
+    <Fixed month="JANUARY" day="6" descriptionPropertiesKey="EPIPHANY"/>
+
+    <!-- Fixed weekday -->
+    <FixedWeekday which="FIRST" weekday="MONDAY" month="MAY" descriptionPropertiesKey="LABOUR_DAY"/>
+
+    <!-- Christian (Easter-based) -->
+    <ChristianHoliday type="CORPUS_CHRISTI"/>
+
+    <!-- Relative to fixed date -->
+    <RelativeToFixed descriptionPropertiesKey="REPENTANCE_PRAYER">
+      <Weekday>WEDNESDAY</Weekday>
+      <When>BEFORE</When>
+      <Date month="NOVEMBER" day="23"/>
+    </RelativeToFixed>
+  </Holidays>
+</SubConfigurations>
+```
+
+## Validity Periods
+
+Regional holidays can have validity periods:
+
+```xml
+<SubConfigurations hierarchy="xx" description="Example Region">
+  <Holidays>
+    <!-- Only valid from 2019 onwards -->
+    <Fixed month="MARCH" day="8" descriptionPropertiesKey="INTERNATIONAL_WOMAN" validFrom="2019"/>
+
+    <!-- Only valid for specific year -->
+    <Fixed month="MAY" day="8" descriptionPropertiesKey="LIBERATION" validFrom="2020" validTo="2020"/>
+
+    <!-- Only valid in specific range -->
+    <Fixed month="OCTOBER" day="31" descriptionPropertiesKey="REFORMATION_DAY" validFrom="2018"/>
+  </Holidays>
+</SubConfigurations>
+```
+
+## Testing Subdivisions
+
+Tests for subdivisions use the `.inSubdivision()` method chained after the holiday assertion:
+
+```java
+import static de.focus_shift.jollyday.core.HolidayCalendar.GERMANY;
+import static de.focus_shift.jollyday.tests.CalendarCheckerApi.assertFor;
+import static java.time.Month.JANUARY;
+
+@Test
+void ensuresBavarianHolidays() {
+  assertFor(GERMANY)
+    .hasFixedHoliday("EPIPHANY", JANUARY, 6).inSubdivision("by").and()
+    .hasFixedHoliday("ALL_SAINTS", NOVEMBER, 1).inSubdivision("by").and()
+    .hasChristianHoliday("CORPUS_CHRISTI").inSubdivision("by").and()
+    .check();
+}
+
+@Test
+void ensuresBadenWurttembergHolidays() {
+  assertFor(GERMANY)
+    .hasFixedHoliday("EPIPHANY", JANUARY, 6).inSubdivision("bw").and()
+    .check();
+}
+
+@Test
+void ensuresNestedSubdivisions() {
+  // Munich is nested within Bavaria (by)
+  assertFor(GERMANY)
+    .hasFixedHoliday("ASSUMPTION_DAY", AUGUST, 15).inSubdivision("by", "mu").and()
+    .check();
+}
+
+@Test
+void ensuresMultipleSubdivisions() {
+  // A holiday can be valid in multiple subdivisions
+  assertFor(GERMANY)
+    .hasFixedHoliday("ALL_SAINTS", NOVEMBER, 1)
+      .inSubdivision("bw")
+      .inSubdivision("by")
+      .inSubdivision("nw")
+      .and()
+    .check();
+}
+```
+
+### inSubdivision() Method Details
+
+- **Signature**: `Properties inSubdivision(final String... subdivisions)`
+- **Usage**: Chain after any holiday assertion method
+- **Multiple subdivisions**: Pass multiple codes as varargs (e.g., `inSubdivision("bw", "by", "nw")`)
+- **Nested subdivisions**: For cities within states, include both codes (e.g., `inSubdivision("by", "mu")` for Munich in Bavaria)
+- **Valid in subdivision**: The method checks that a holiday is present in the specified subdivision(s)
+
+### Example from HolidayDETest.java
+
+```java
+@Test
+void ensuresAllHolidaysFor2024() {
+  assertFor(GERMANY)
+    // National holidays (all of Germany)
+    .hasFixedHoliday("NEW_YEAR", JANUARY, 1).and()
+    .hasFixedHoliday("LABOUR_DAY", MAY, 1).and()
+    .hasFixedHoliday("CHRISTMAS", DECEMBER, 25).and()
+    
+    // Baden-Württemberg specific holidays
+    .hasFixedHoliday("EPIPHANY", JANUARY, 6).inSubdivision("bw").and()
+    .hasFixedHoliday("ALL_SAINTS", NOVEMBER, 1).inSubdivision("bw").and()
+    .hasChristianHoliday("CORPUS_CHRISTI").inSubdivision("bw").and()
+    
+    // Bavaria specific holidays
+    .hasFixedHoliday("EPIPHANY", JANUARY, 6).inSubdivision("by").and()
+    .hasFixedHoliday("ALL_SAINTS", NOVEMBER, 1).inSubdivision("by").and()
+    .hasChristianHoliday("CORPUS_CHRISTI").inSubdivision("by").and()
+    
+    // Munich (nested within Bavaria)
+    .hasFixedHoliday("ASSUMPTION_DAY", AUGUST, 15).inSubdivision("by", "mu").and()
+    
+    .check();
+}
+```
+
+## Best Practices
+
+1. **Use ISO codes**: Always use official ISO 3166-2 subdivision codes
+2. **Clear descriptions**: Include the full region name in the `description` attribute
+3. **Document sources**: Add `<Sources>` elements for regional holiday references
+4. **Nested when appropriate**: Use nested SubConfigurations for cities within states
+5. **Consistent ordering**: Place SubConfigurations after the main `<Holidays>` section
+6. **Validity periods**: Use `validFrom`/`validTo` for historical accuracy
+
+## Common Subdivision Examples
+
+### United States (California)
+
+```xml
+<SubConfigurations hierarchy="CA" description="California">
+  <Holidays>
+    <Fixed month="JANUARY" day="1" descriptionPropertiesKey="NEW_YEAR"/>
+    <FixedWeekday which="THIRD" weekday="MONDAY" month="JANUARY" descriptionPropertiesKey="MLK_DAY"/>
+  </Holidays>
+</SubConfigurations>
+```
+
+### Germany (Bavaria)
+
+```xml
+<SubConfigurations hierarchy="by" description="Bavaria">
+  <Holidays>
+    <Fixed month="JANUARY" day="6" descriptionPropertiesKey="EPIPHANY"/>
+    <Fixed month="NOVEMBER" day="1" descriptionPropertiesKey="ALL_SAINTS"/>
+    <ChristianHoliday type="CORPUS_CHRISTI"/>
+  </Holidays>
+</SubConfigurations>
+```
+
+### France (Corsica)
+
+```xml
+<SubConfigurations hierarchy="2C" description="Corsica">
+  <Holidays>
+    <Fixed month="MAY" day="15" descriptionPropertiesKey="CORSICA_LIBERATION"/>
+  </Holidays>
+</SubConfigurations>
+```
+
+## ISO 3166-2 Reference
+
+| Country       | ISO Code | Subdivision Codes                                              |
+|---------------|----------|----------------------------------------------------------------|
+| Germany       | DE       | be, bb, bw, by, hb, he, hh, mv, ni, nw, rp, sl, sn, st, sh, th |
+| United States | US       | CA, NY, TX, FL, ... (state codes)                              |
+| France        | FR       | 01, 02, ... (department codes)                                 |
+| Austria       | AT       | WI, B, K, ... (state codes)                                    |
+
+**Sources**: https://en.wikipedia.org/wiki/ISO_3166-2
diff --git a/.agents/skills/how-to-add-a-new-holiday-calendar-for-a-country/SKILL.md b/.agents/skills/how-to-add-a-new-holiday-calendar-for-a-country/SKILL.md
@@ -1,459 +0,0 @@
----
-name: add-holiday-calendar
-description: Guide for adding new country holiday calendars to Jollyday, including XML configuration, holiday definitions, description properties, and test coverage
----
-
-# How to Add a New Holiday Calendar for a Country
-
-This guide explains how to add a new country's holiday calendar to Jollyday based on existing implementations and pull requests.
-
-## Overview
-
-Jollyday stores holiday calendars as XML files in `jollyday-core/src/main/resources/holidays/`. Each country has its own file named `Holidays_[country_code].xml`.
-
-## Step 1: Create the Holiday Calendar File
-
-Create a new file `jollyday-core/src/main/resources/holidays/Holidays_[country_code].xml` with the following structure:
-
-```xml
-<?xml version="1.0" encoding="UTF-8"?>
-
-<Configuration hierarchy="[country_code]" description="[Country Name]"
-               xmlns="https://focus_shift.de/jollyday/schema/holiday"
-               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
-               xsi:schemaLocation="https://focus_shift.de/jollyday/schema/holiday https://focus_shift.de/jollyday/schema/holiday/holiday.xsd">
-  <Holidays>
-    <!-- Add your holidays here -->
-  </Holidays>
-
-  <Sources>
-    <Source>[URL to official source or Wikipedia]</Source>
-    <Source of="ISO 3166">[URL to official iso 3166 source]</Source>
-    <Source of="ISO 3166-2">[URL to official iso 3166-2 source for subdivisions]</Source>
-  </Sources>
-</Configuration>
-```
-
-### Root Element Attributes
-
-| Attribute     | Description                                              |
-|---------------|----------------------------------------------------------|
-| `hierarchy`   | ISO 3166-1 alpha-2 country code (e.g., "de", "us", "fr") |
-| `description` | Full country name in English                             |
-
-## Step 2: Add Holiday Definitions
-
-### Fixed Date Holidays
-
-For holidays on a fixed calendar date:
-
-```xml
-<Fixed month="JANUARY" day="1" descriptionPropertiesKey="NEW_YEAR"/>
-```
-
-With validity period:
-
-```xml
-<Fixed month="OCTOBER" day="31" validFrom="2017" descriptionPropertiesKey="REFORMATION_DAY"/>
-<Fixed month="JUNE" day="19" validFrom="2021" descriptionPropertiesKey="JUNETEENTH"/>
-<Fixed month="OCTOBER" day="31" validFrom="2017" validTo="2017" descriptionPropertiesKey="REFORMATION_DAY"/>
-```
-
-### Fixed Weekday Holidays
-
-For holidays on a specific weekday in a month:
-
-```xml
-<FixedWeekday which="FIRST" weekday="MONDAY" month="SEPTEMBER" validFrom="1895" descriptionPropertiesKey="LABOUR_DAY"/>
-<FixedWeekday which="THIRD" weekday="MONDAY" month="JANUARY" validFrom="1986" descriptionPropertiesKey="MARTIN_LUTHER_KING"/>
-<FixedWeekday which="FOURTH" weekday="THURSDAY" month="NOVEMBER" validFrom="1863" descriptionPropertiesKey="THANKSGIVING"/>
-<FixedWeekday which="LAST" weekday="MONDAY" month="MAY" validFrom="1968" descriptionPropertiesKey="MEMORIAL_DAY"/>
-```
-
-**`which` values**: `FIRST`, `SECOND`, `THIRD`, `FOURTH`, `LAST`
-
-### Christian Movable Holidays
-
-For Christian holidays that depend on Easter:
-
-```xml
-<ChristianHoliday type="GOOD_FRIDAY"/>
-<ChristianHoliday type="EASTER_MONDAY"/>
-<ChristianHoliday type="ASCENSION_DAY"/>
-<ChristianHoliday type="WHIT_MONDAY"/>
-<ChristianHoliday type="CORPUS_CHRISTI"/>
-<ChristianHoliday type="PENTECOST"/>
-```
-
-With optional `localizedType` for observance holidays:
-
-```xml
-<ChristianHoliday type="GOOD_FRIDAY" localizedType="OBSERVANCE"/>
-```
-
-### Islamic Holidays
-
-For Islamic calendar-based holidays:
-
-```xml
-<IslamicHoliday type="JUMUATUL_WIDA"/>
-<IslamicHoliday type="RAMADAN_END"/>
-<IslamicHoliday type="ID_AL_FITR"/>
-<IslamicHoliday type="ID_AL_FITR_2"/>
-<IslamicHoliday type="ID_AL_FITR_3"/>
-<IslamicHoliday type="ARAFAAT"/>
-<IslamicHoliday type="ID_UL_ADHA"/>
-<IslamicHoliday type="ID_UL_ADHA_2"/>
-<IslamicHoliday type="ID_UL_ADHA_3"/>
-<IslamicHoliday type="NEWYEAR"/>
-<IslamicHoliday type="MAWLID_AN_NABI"/>
-```
-
-### Holidays Relative to Fixed Dates
-
-For holidays calculated relative to a fixed date:
-
-```xml
-<RelativeToFixed validFrom="1990" descriptionPropertiesKey="REPENTANCE_PRAYER">
-  <Weekday>WEDNESDAY</Weekday>
-  <When>BEFORE</When>
-  <Date month="NOVEMBER" day="23"/>
-</RelativeToFixed>
-```
-
-**`When` values**: `BEFORE`, `AFTER`
-
-### Holidays Relative to Other Weekday Holidays
-
-For holidays calculated relative to another moving holiday:
-
-```xml
-<RelativeToWeekdayInMonth weekday="FRIDAY" when="BEFORE" descriptionPropertiesKey="SERVICE_REDUCTION">
-  <FixedWeekday which="LAST" weekday="MONDAY" month="MAY"/>
-</RelativeToWeekdayInMonth>
-```
-
-### Moving Conditions
-
-For holidays that shift to weekdays when falling on weekends:
-
-```xml
-<Fixed month="JANUARY" day="1" descriptionPropertiesKey="NEW_YEAR">
-  <MovingCondition substitute="SATURDAY" with="PREVIOUS" weekday="FRIDAY"/>
-  <MovingCondition substitute="SUNDAY" with="NEXT" weekday="MONDAY"/>
-</Fixed>
-```
-
-## Step 3: Add Description Properties
-
-Add entries to `jollyday-core/src/main/resources/descriptions/holiday_descriptions.properties`:
-
-```properties
-holiday.description.NEW_YEAR                    = New Year's Day
-holiday.description.LABOUR_DAY                  = Labour Day
-holiday.description.CHRISTMAS                   = Christmas
-holiday.description.Independence_DAY            = Independence Day
-holiday.description.NATIONAL_DAY                = National Day
-```
-
-### Key Naming Conventions
-
-- Use UPPERCASE with underscores: `NEW_YEAR`, `LABOUR_DAY`, `GOOD_FRIDAY`
-- For multi-word holidays: `FIRST_CHRISTMAS_DAY`, `SECOND_CHRISTMAS_DAY`
-- Country-specific: `REFORMATION_DAY`, `UNIFICATION_GERMANY`, `MARTIN_LUTHER_KING`
-
-### Localized Descriptions
-
-Add entries to locale-specific files:
-
-- `holiday_descriptions_de.properties` (German)
-- `holiday_descriptions_fr.properties` (French)
-- `holiday_descriptions_es.properties` (Spanish)
-- `holiday_descriptions_pt.properties` (Portuguese)
-- `holiday_descriptions_nl.properties` (Dutch)
-- `holiday_descriptions_sv.properties` (Swedish)
-- `holiday_descriptions_el.properties` (Greek)
-
-## Step 4: Add Country Description
-
-Add the country name to `jollyday-core/src/main/resources/descriptions/country_descriptions.properties`:
-
-```properties
-country.description.xx = Your Country Name
-```
-
-And localized versions if applicable.
-
-## Step 5: Add Regional/Subdivision Holidays
-
-For countries with regional holidays (states, provinces):
-
-```xml
-<SubConfigurations hierarchy="[region_code]" description="[Region Name]">
-  <Holidays>
-    <Fixed month="MARCH" day="8" descriptionPropertiesKey="INTERNATIONAL_WOMAN" validFrom="2019"/>
-  </Holidays>
-</SubConfigurations>
-```
-
-Example with nested subdivisions:
-
-```xml
-<SubConfigurations hierarchy="by" description="Bavaria">
-  <Holidays>
-    <Fixed month="JANUARY" day="6" descriptionPropertiesKey="EPIPHANY"/>
-  </Holidays>
-
-  <SubConfigurations hierarchy="mu" description="Munich">
-    <Holidays>
-      <Fixed day="15" month="AUGUST" descriptionPropertiesKey="ASSUMPTION_DAY"/>
-    </Holidays>
-  </SubConfigurations>
-</SubConfigurations>
-```
-
-## Step 6: Add Test Coverage
-
-Create a test in `jollyday-tests/src/test/java/de/focus_shift/jollyday/tests/country/` using the `CalendarCheckerApi`:
-
-```java
-package de.focus_shift.jollyday.tests.country;
-
-import org.junit.jupiter.api.Test;
-
-import java.time.Year;
-
-import static de.focus_shift.jollyday.core.HolidayCalendar.YOUR_COUNTRY; // The HolidayCalendar constant for your country
-import static de.focus_shift.jollyday.tests.CalendarCheckerApi.assertFor;
-import static java.time.Month.JANUARY;
-import static java.time.Month.DECEMBER;
-
-class HolidaysXXTest { // Replace XX with your country code
-
-  @Test
-  void ensuresHolidays() {
-    assertFor(YOUR_COUNTRY)
-      .hasFixedHoliday("NEW_YEAR", JANUARY, 1).and()
-      .hasFixedHoliday("CHRISTMAS", DECEMBER, 25).and()
-      .hasFixedHoliday("SECOND_CHRISTMAS_DAY", DECEMBER, 26)
-        .validFrom(Year.of(1990))
-      .and()
-      .hasChristianHoliday("GOOD_FRIDAY").and()
-      .hasChristianHoliday("EASTER_MONDAY")
-        .validFrom(Year.of(2000))
-      .check();
-  }
-}
-```
-
-### CalendarCheckerApi Methods
-
-| Method                             | Description                                 |
-|------------------------------------|---------------------------------------------|
-| `hasFixedHoliday(key, month, day)` | Checks for a fixed date holiday             |
-| `hasChristianHoliday(key)`         | Checks for a Christian/Easter-based holiday |
-| `hasIslamicHoliday(key)`           | Checks for an Islamic calendar holiday      |
-| `hasEthiopianOrthodoxHoliday(key)` | Checks for Ethiopian Orthodox holiday       |
-| `validFrom(Year)`                  | Specifies the starting year                 |
-| `validTo(Year)`                    | Specifies the ending year                   |
-| `validBetween(Year, Year)`         | Specifies a valid year range                |
-| `notValidBetween(Year, Year)`      | Specifies an invalid year range             |
-| `inSubdivision(...codes)`          | For regional/state-specific holidays        |
-| `and()`                            | Chains another holiday assertion            |
-| `check()`                          | Performs the assertions                     |
-
-### Example with Subdivisions
-
-```java
-@Test
-void ensuresHolidays() {
-  assertFor(YOUR_COUNTRY)
-    .hasFixedHoliday("NEW_YEAR", JANUARY, 1).and()
-    .hasFixedHoliday("REGIONAL_HOLIDAY", MARCH, 8)
-      .inSubdivision("state-code")
-      .validFrom(Year.of(2020))
-    .and()
-    .check();
-}
-```
-
-## Complete Example: Germany (Simplified)
-
-```xml
-<?xml version="1.0" encoding="UTF-8"?>
-
-<Configuration hierarchy="de" description="Germany"
-               xmlns="https://focus_shift.de/jollyday/schema/holiday"
-               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
-               xsi:schemaLocation="https://focus_shift.de/jollyday/schema/holiday https://focus_shift.de/jollyday/schema/holiday/holiday.xsd">
-  <Holidays>
-    <Fixed month="JANUARY" day="1" descriptionPropertiesKey="NEW_YEAR"/>
-    <Fixed month="MAY" day="1" descriptionPropertiesKey="LABOUR_DAY"/>
-    <Fixed month="DECEMBER" day="25" descriptionPropertiesKey="FIRST_CHRISTMAS_DAY"/>
-    <Fixed month="DECEMBER" day="26" descriptionPropertiesKey="SECOND_CHRISTMAS_DAY"/>
-    <ChristianHoliday type="GOOD_FRIDAY"/>
-    <ChristianHoliday type="EASTER_MONDAY"/>
-    <ChristianHoliday type="ASCENSION_DAY"/>
-    <ChristianHoliday type="WHIT_MONDAY"/>
-  </Holidays>
-
-  <Sources>
-    <Source>https://en.wikipedia.org/wiki/Public_holidays_in_Germany</Source>
-    <Source of="ISO 3166">https://www.iso.org/obp/ui/#iso:code:3166:DE</Source>
-    <Source of="ISO 3166-2">https://en.wikipedia.org/wiki/ISO_3166-2:DE</Source>
-  </Sources>
-</Configuration>
-```
-
-## Common Attributes Reference
-
-| Attribute                  | Description                | Example                  |
-|----------------------------|----------------------------|--------------------------|
-| `month`                    | Month (English, uppercase) | `JANUARY`, `DECEMBER`    |
-| `day`                      | Day of month               | `1`, `25`                |
-| `weekday`                  | Day of week                | `MONDAY`, `FRIDAY`       |
-| `which`                    | Which occurrence           | `FIRST`, `LAST`, `THIRD` |
-| `validFrom`                | Start year                 | `1990`, `2021`           |
-| `validTo`                  | End year                   | `1990`, `2020`           |
-| `descriptionPropertiesKey` | Key for description        | `NEW_YEAR`               |
-| `localizedType`            | Holiday type variant       | `OBSERVANCE`             |
-
-## Available Month Values
-
-`JANUARY`, `FEBRUARY`, `MARCH`, `APRIL`, `MAY`, `JUNE`, `JULY`, `AUGUST`, `SEPTEMBER`, `OCTOBER`, `NOVEMBER`, `DECEMBER`
-
-## Available Weekday Values
-
-`MONDAY`, `TUESDAY`, `WEDNESDAY`, `THURSDAY`, `FRIDAY`, `SATURDAY`, `SUNDAY`
-
-## Available ChristianHoliday Types
-
-- `GOOD_FRIDAY`
-- `EASTER`
-- `EASTER_MONDAY`
-- `EASTER_SATURDAY`
-- `EASTER_TUESDAY`
-- `ASCENSION_DAY`
-- `WHIT_MONDAY`
-- `PENTECOST`
-- `PENTECOST_MONDAY`
-- `CORPUS_CHRISTI`
-- `CARNIVAL`
-- `MARDI_GRAS`
-- `MAUNDY_THURSDAY`
-- `ASH_WEDNESDAY`
-
-## Available IslamicHoliday Types
-
-- `NEWYEAR`
-- `MAWLID_AN_NABI`
-- `LAILAT_AL_BARAT`
-- `LAILAT_AL_MIRAJ`
-- `LAILAT_AL_QADR`
-- `ASCHURA`
-- `RAMADAN`
-- `RAMADAN_END`
-- `ID_AL_FITR`, `ID_AL_FITR_2`, `ID_AL_FITR_3`
-- `ARAFAAT`
-- `ID_UL_ADHA`, `ID_UL_ADHA_2`, `ID_UL_ADHA_3`
-
-## Step 7: Register the Calendar in HolidayCalendar.java
-
-Add the new calendar to `jollyday-core/src/main/java/de/focus_shift/jollyday/core/HolidayCalendar.java`.
-
-### Organization Pattern
-
-The `HolidayCalendar` enum follows a strict organization pattern:
-- Calendars are listed in **alphabetical order** by their ISO country code
-- Each line starts with calendars beginning with a specific letter (A, B, C, etc.)
-- Multiple calendars sharing the same starting letter are grouped on the same line
-
-### Example Structure
-
-```java
-public enum HolidayCalendar {
-  ANTARCTICA("AQ"), ALBANIA("AL"), ANDORRA("AD"), ARGENTINA("AR"), ARMENIA("AM"), AUSTRALIA("AU"), AUSTRIA("AT"),
-  BAHAMAS("BS"), BELARUS("BY"), BELGIUM("BE"), BERMUDA("BM"), ...
-  CANADA(Locale.CANADA.getCountry()), CAYMAN_ISLANDS("KY"), ...
-}
-```
-
-### Adding Your Calendar
-
-1. Find the line that starts with the appropriate letter for your country code
-2. Add your calendar in alphabetical order on that line
-3. Use the format: `CALENDAR_NAME("ISO_CODE")`
-
-**Example for adding Antarctica (AQ):**
-- Find line starting with "A" calendars
-- Insert `ANTARCTICA("AQ"),` in alphabetical position
-
-**Example for a fictional "Zebra" (ZB):**
-- Add to the "Z" line: `ZEBRA("ZB"), ZIMBABWE("ZW");`
-
-## References
-
-- Schema: `https://focus_shift.de/jollyday/schema/holiday/holiday.xsd`
-- XSD Location in repo: `jollyday-core/src/main/resources/focus_shift.de/jollyday/schema/holiday/holiday.xsd`
-- Examples: Review existing `Holidays_*.xml` files in `jollyday-core/src/main/resources/holidays/`
-
-## Running Tests
-
-### Prerequisites
-
-**Java Version**: This project requires **Java 17**. The project uses [asdf](https://asdf-vm.com/) for version management.
-
-Before running tests, ensure you have Java 17 available:
-
-```bash
-# Verify Java version
-java -version
-# Should output: openjdk version "17.x.x"
-```
-
-**Note**: If you don't have asdf installed:
-1. Install asdf: https://asdf-vm.com/guide/getting-started.html
-2. Install Java: `asdf install`
-
-### Build the Project
-
-Before running tests, ensure the verify phase has been executed:
-
-```bash
-./mvnw verify -DskipTests
-```
-
-### Run Country-Specific Test
-
-Run the test for your specific country:
-
-```bash
-./mvnw test -Dtest=HolidayXXTest -pl jollyday-tests
-```
-
-Replace `XX` with your country code in **uppercase** (e.g., `HolidayDETest` for Germany, `HolidayGITest` for Gibraltar).
-
-**Test naming convention**: `Holiday` + uppercase country code + `Test`
-
-**Examples**:
-- Germany: `./mvnw test -Dtest=HolidayDETest -pl jollyday-tests`
-- Gibraltar: `./mvnw test -Dtest=HolidayGITest -pl jollyday-tests`
-- United States: `./mvnw test -Dtest=HolidayUSTest -pl jollyday-tests`
-
-### Full Test Suite
-
-To run all tests:
-
-```bash
-./mvnw test
-```
-
-### Test Output Format
-
-A successful test run looks like:
-
-```
-[INFO] Running de.focus_shift.jollyday.tests.country.HolidayDETest
-[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
-[INFO] BUILD SUCCESS
-```
diff --git a/.agents/skills/register-holiday-calendar/SKILL.md b/.agents/skills/register-holiday-calendar/SKILL.md
@@ -0,0 +1,109 @@
+---
+name: register-holiday-calendar
+description: Register a new holiday calendar in the HolidayCalendar enum
+---
+
+# How to Register a Holiday Calendar
+
+This guide explains how to register a new country calendar in the `HolidayCalendar` enum.
+
+## File Location
+
+Edit: `jollyday-core/src/main/java/de/focus_shift/jollyday/core/HolidayCalendar.java`
+
+## Organization Pattern
+
+The `HolidayCalendar` enum follows a strict organization pattern:
+
+1. Calendars are listed in **alphabetical order** by their ISO country code
+2. Each line starts with calendars beginning with a specific letter (A, B, C, etc.)
+3. Multiple calendars sharing the same starting letter are grouped on the same line
+
+## Example Structure
+
+```java
+public enum HolidayCalendar {
+  ANTARCTICA("AQ"), ALBANIA("AL"), ANDORRA("AD"), ARGENTINA("AR"), ARMENIA("AM"), AUSTRALIA("AU"), AUSTRIA("AT"),
+  BAHAMAS("BS"), BELARUS("BY"), BELGIUM("BE"), BERMUDA("BM"), BOLIVIA("BO"), BRAZIL("BR"), ...
+  CANADA(Locale.CANADA.getCountry()), CAYMAN_ISLANDS("KY"), ...
+  GERMANY("DE"), GREECE("GR"), ...
+  UNITED_STATES(Locale.US.getCountry()), ...
+}
+```
+
+## Steps to Add Your Calendar
+
+### 1. Find the Correct Line
+
+Identify which line your country code should appear on based on the first letter:
+
+| First Letter | Example Calendars                                  |
+|--------------|----------------------------------------------------|
+| A            | ANTARCTICA, ALBANIA, ANDORRA, ARGENTINA, AUSTRALIA |
+| B            | BELARUS, BELGIUM, BERMUDA, BRAZIL                  |
+| D            | DENMARK, DOMINICAN, ECUADAR (E starts D line)      |
+
+### 2. Insert in Alphabetical Order
+
+Add your calendar in alphabetical position within that letter group:
+
+**Before:**
+```java
+ALBANIA("AL"), ANDORRA("AD"), ARGENTINA("AR"),
+```
+
+**Adding Antarctica (AQ) - after ARGENTINA:**
+```java
+ALBANIA("AL"), ANDORRA("AD"), ARGENTINA("AR"), ANTARCTICA("AQ"),
+```
+
+### 3. Use Correct Format
+
+Format: `COUNTRY_NAME("ISO_CODE")`
+
+**Examples:**
+```java
+GERMANY("DE"),                    // Direct ISO code
+CANADA(Locale.CANADA.getCountry()), // Java Locale for special cases
+UNITED_STATES(Locale.US.getCountry()), // Java Locale for US
+```
+
+## Complete Example
+
+Adding a fictional "Zebra" country with code "ZB":
+
+**Before:**
+```java
+  ZIMBABWE("ZW");
+}
+```
+
+**After:**
+```java
+  ZEBRA("ZB"), ZIMBABWE("ZW");
+}
+```
+
+## Special Cases
+
+Some countries use Java Locale instead of string codes:
+
+```java
+CANADA(Locale.CANADA.getCountry()),  // Returns "CA"
+UNITED_STATES(Locale.US.getCountry()),  // Returns "US"
+```
+
+## Best Practices
+
+1. **Alphabetical order**: Always maintain alphabetical order by ISO code
+2. **Proper naming**: Use full country name in uppercase with underscores
+3. **ISO code**: Use the official ISO 3166-1 alpha-2 code
+4. **Comma placement**: Add comma after each entry except the last
+5. **Semicolon**: Last entry ends with semicolon before closing brace
+
+## Verification
+
+After adding your calendar, verify:
+1. The calendar is in the correct alphabetical position
+2. The ISO code matches the XML file's hierarchy attribute
+3. The Java file compiles without errors
diff --git a/.agents/skills/write-holiday-tests/SKILL.md b/.agents/skills/write-holiday-tests/SKILL.md
@@ -0,0 +1,189 @@
+---
+name: write-holiday-tests
+description: Write country-specific holiday tests using CalendarCheckerApi
+---
+
+# How to Write Holiday Tests
+
+This guide explains how to write tests for new or modified holiday calendars using the `CalendarCheckerApi`.
+
+## File Location
+
+Create test file at: `jollyday-tests/src/test/java/de/focus_shift/jollyday/tests/[CountryName]Test.java`
+
+**Example naming:**
+- Germany: `HolidayDETest.java`
+- United States: `HolidayUSTest.java`
+- France: `HolidayFRTest.java`
+
+## CalendarCheckerApi
+
+The `CalendarCheckerApi` provides fluent assertions for testing holidays:
+
+```java
+import static de.focus_shift.jollyday.tests.CalendarCheckerApi.assertFor;
+import static de.focus_shift.jollyday.core.HolidayCalendar.GERMANY;
+import static java.time.Month.JANUARY;
+import static java.time.Month.FEBRUARY;
+```
+
+### Basic Usage
+
+```java
+@Test
+void ensuresHolidays() {
+  assertFor(GERMANY)
+    .hasFixedHoliday("NEW_YEAR", JANUARY, 1).and()
+    .hasChristianHoliday("GOOD_FRIDAY").and()
+    .check();
+}
+```
+
+## Assertion Methods
+
+### Fixed Date Holidays
+
+```java
+// Basic fixed holiday
+.hasFixedHoliday("NEW_YEAR", JANUARY, 1)
+
+// With validFrom year
+.hasFixedHoliday("JUNETEENTH", JUNE, 19, 2021)
+
+// With validFrom and validTo
+.hasFixedHoliday("REFORMATION_DAY", OCTOBER, 31, 2017, null)
+```
+
+### Fixed Weekday Holidays
+
+```java
+// First Monday in September
+.hasFixedWeekdayHoliday("LABOUR_DAY", java.time.DayOfWeek.MONDAY, SEPTEMBER, java.time.temporal.TemporalAdjusters.firstInMonth(java.time.DayOfWeek.MONDAY))
+
+// Third Monday in January (MLK Day)
+.hasFixedWeekdayHoliday("MARTIN_LUTHER_KING", JANUARY, 3)
+```
+
+### Christian (Easter-based) Holidays
+
+```java
+.hasChristianHoliday("GOOD_FRIDAY")
+.hasChristianHoliday("EASTER_MONDAY")
+.hasChristianHoliday("ASCENSION_DAY")
+.hasChristianHoliday("WHIT_MONDAY")
+.hasChristianHoliday("CORPUS_CHRISTI")
+```
+
+### Islamic Calendar Holidays
+
+```java
+.hasIslamicHoliday("ID_AL_FITR", 2024, 10, 10)  // type, year, month, day
+.hasIslamicHoliday("ID_UL_ADHA", 2024, 6, 16)
+.hasIslamicHoliday("NEWYEAR", 2024, 7, 7)
+```
+
+### Regional/Subdivision Holidays
+
+```java
+// Holiday in specific region
+.hasSubConfig("bw")
+  .hasFixedHoliday("REPELLENCE_PRAYER", NOVEMBER, 20)
+  .and()
+.check();
+
+// Multiple regions
+.hasSubConfig("by")
+  .hasFixedHoliday("EPIPHANY", JANUARY, 6)
+  .and()
+.hasSubConfig("bw")
+  .hasFixedHoliday("EPIPHANY", JANUARY, 6)
+  .and()
+.check();
+```
+
+### Not a Holiday
+
+```java
+.notHasHoliday(DECEMBER, 31)
+.notHasSubConfig("bw")
+  .hasFixedHoliday("SOME_HOLIDAY", DECEMBER, 24)
+  .and()
+.check();
+```
+
+## Complete Test Example
+
+```java
+package de.focus_shift.jollyday.tests;
+
+import de.focus_shift.jollyday.core.HolidayCalendar;
+import org.junit.jupiter.api.Test;
+
+import static de.focus_shift.jollyday.tests.CalendarCheckerApi.assertFor;
+import static java.time.Month.*;
+
+class HolidayGETest {
+
+  @Test
+  void ensuresHolidays() {
+    assertFor(HolidayCalendar.GERMANY)
+      // National holidays
+      .hasFixedHoliday("NEW_YEAR", JANUARY, 1)
+      .hasChristianHoliday("GOOD_FRIDAY")
+      .hasChristianHoliday("EASTER_MONDAY")
+      .hasFixedHoliday("LABOUR_DAY", MAY, 1)
+      .hasChristianHoliday("ASCENSION_DAY")
+      .hasChristianHoliday("WHIT_MONDAY")
+      .hasFixedHoliday("CHRISTMAS", DECEMBER, 25)
+      .hasFixedHoliday("SECOND_CHRISTMAS_DAY", DECEMBER, 26)
+      .and()
+      // Regional holidays - Bavaria
+      .hasSubConfig("by")
+      .hasFixedHoliday("EPIPHANY", JANUARY, 6)
+      .hasFixedHoliday("ASCENSION_DAY", MAY)
+      .and()
+      // Regional holidays - Baden-Württemberg
+      .hasSubConfig("bw")
+      .hasFixedHoliday("EPIPHANY", JANUARY, 6)
+      .hasFixedHoliday("REPELLENCE_PRAYER", NOVEMBER)
+      .and()
+      .check();
+  }
+}
+```
+
+## Testing Edge Cases
+
+### Moving Conditions (Weekend Shift)
+
+```java
+@Test
+void ensuresMovingCondition() {
+  assertFor(HolidayCalendar.US)
+    // New Year falls on Saturday, shifts to Friday
+    .hasFixedHoliday("NEW_YEAR", JANUARY, 1, 2023)
+    .check();
+}
+```
+
+### Historical Changes
+
+```java
+@Test
+void ensuresHistoricalChanges() {
+  assertFor(HolidayCalendar.GERMANY)
+    // Reformation Day only since 2017
+    .hasFixedHoliday("REFORMATION_DAY", OCTOBER, 31, 2017)
+    .notHasHoliday(OCTOBER, 31, 2016)
+    .check();
+}
+```
+
+## Best Practices
+
+1. **Comprehensive coverage**: Test all holidays including regional ones
+2. **Valid ranges**: Test holidays with `validFrom`/`validTo` constraints
+3. **Edge cases**: Test years where holidays fall on weekends
+4. **Clear naming**: Use descriptive test method names
+5. **Group related tests**: Use `.and()` to chain related assertions
+
diff --git a/agents.md b/agents.md
@@ -0,0 +1,362 @@
+---
+name: jollyday
+description: A Java library for querying public holidays supporting 110+ countries with XML-based holiday calendar configuration
+---
+
+# Jollyday - Public Holiday Library
+
+## Project Overview
+
+**Jollyday** is a Java library to query public holidays. It currently supports **over 110 countries**. The holiday data is stored in XML files (one for each country) and will be read from the classpath.
+
+### Key Features
+
+- Supports 110+ countries with public holiday data
+- ISO 3166-1 alpha-2 country code support
+- ISO 3166-2 subdivision support (states, provinces, regions)
+- Multiple holiday types: Fixed dates, moving holidays (Easter-based, Islamic calendar, etc.)
+- XML-based configuration with validation via XSD
+- Supports JAXB and Jackson for XML unmarshalling
+- Java 17+ required
+
+### Modules
+
+| Module             | Description                                    |
+|--------------------|------------------------------------------------|
+| `jollyday-core`    | Core API, holiday data, parser implementations |
+| `jollyday-jackson` | Jackson XML binding implementation             |
+| `jollyday-jaxb`    | Jakarta XML Binding implementation             |
+| `jollyday-tests`   | Integration and country-specific tests         |
+
+## Architecture
+
+```
+jollyday/
+├── jollyday-core/
+│   ├── src/main/java/de/focus_shift/jollyday/core/
+│   │   ├── Holiday.java                 # Holiday value object
+│   │   ├── HolidayManager.java          # Main API entry point
+│   │   ├── HolidayCalendar.java         # Enum of all supported countries
+│   │   ├── ManagerParameters.java       # Configuration builder
+│   │   ├── impl/                        # Manager implementations
+│   │   ├── parser/                      # Holiday parsing API
+│   │   │   └── impl/                    # Parser implementations
+│   │   └── spi/                         # Holiday configuration interfaces
+│   └── src/main/resources/
+│       ├── holidays/                    # Country holiday XML files
+│       ├── descriptions/                # Localized holiday descriptions
+│       ├── focus_shift.de/jollyday/     # XSD schema definition
+│       └── jollyday.properties          # Default configuration
+├── jollyday-jackson/                    # Jackson XML unmarshalling
+├── jollyday-jaxb/                       # JAXB XML unmarshalling
+└── jollyday-tests/                      # Test suite
+```
+
+## Key Concepts
+
+### Holiday Types
+
+| Type                         | Description                          | Examples                                        |
+|------------------------------|--------------------------------------|-------------------------------------------------|
+| **Fixed**                    | Same calendar date every year        | New Year (Jan 1), Christmas (Dec 25)            |
+| **FixedWeekday**             | Specific weekday occurrence in month | Labor Day (first Monday in Sept)                |
+| **ChristianHoliday**         | Easter-based moving holidays         | Good Friday, Easter Monday, Ascension           |
+| **IslamicHoliday**           | Islamic calendar holidays            | Eid al-Fitr, Eid al-Adha                        |
+| **EthiopianOrthodoxHoliday** | Ethiopian Orthodox holidays          | Timkat, Meskel                                  |
+| **RelativeToFixed**          | Relative to a fixed date             | German Repentance Day (Wednesday before Nov 23) |
+| **RelativeToWeekdayInMonth** | Relative to a moving holiday         | Various country-specific holidays               |
+
+### Holiday Categories
+
+| Category           | Description                                 |
+|--------------------|---------------------------------------------|
+| **Public Holiday** | Official non-working days (paid time off)   |
+| **Bank Holiday**   | Days when financial institutions are closed |
+| **Observance**     | Celebrations without official time off      |
+
+### ISO Standards
+
+- **ISO 3166-1 alpha-2**: Country codes (e.g., `DE`, `US`, `FR`)
+- **ISO 3166-2**: Subdivision codes (e.g., `DE-BY` for Bavaria, Germany)
+
+## XML Holiday Configuration
+
+### Root Structure
+
+```xml
+<?xml version="1.0" encoding="UTF-8"?>
+
+<Configuration hierarchy="[country_code]" description="[Country Name]"
+               xmlns="https://focus_shift.de/jollyday/schema/holiday"
+               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
+               xsi:schemaLocation="https://focus_shift.de/jollyday/schema/holiday https://focus_shift.de/jollyday/schema/holiday/holiday.xsd">
+  <Holidays>
+    <!-- National holidays -->
+  </Holidays>
+
+  <Sources>
+    <Source>https://en.wikipedia.org/wiki/Public_holidays_in_[Country]</Source>
+    <Source of="ISO 3166">https://www.iso.org/obp/ui/#iso:code:3166:[CODE]</Source>
+  </Sources>
+</Configuration>
+```
+
+### Holiday Elements
+
+#### Fixed Date
+```xml
+<Fixed month="JANUARY" day="1" descriptionPropertiesKey="NEW_YEAR"/>
+<Fixed month="DECEMBER" day="25" validFrom="1990" descriptionPropertiesKey="CHRISTMAS"/>
+```
+
+#### Fixed Weekday in Month
+```xml
+<FixedWeekday which="FIRST" weekday="MONDAY" month="SEPTEMBER" descriptionPropertiesKey="LABOUR_DAY"/>
+<FixedWeekday which="LAST" weekday="MONDAY" month="MAY" descriptionPropertiesKey="MEMORIAL_DAY"/>
+```
+- `which`: FIRST, SECOND, THIRD, FOURTH, LAST
+
+#### Christian (Easter-based)
+```xml
+<ChristianHoliday type="GOOD_FRIDAY"/>
+<ChristianHoliday type="EASTER_MONDAY"/>
+<ChristianHoliday type="ASCENSION_DAY"/>
+<ChristianHoliday type="WHIT_MONDAY"/>
+<ChristianHoliday type="CORPUS_CHRISTI"/>
+```
+
+#### Islamic Calendar
+```xml
+<IslamicHoliday type="ID_AL_FITR"/>
+<IslamicHoliday type="ID_UL_ADHA"/>
+<IslamicHoliday type="NEWYEAR"/>
+```
+
+#### Relative to Fixed Date
+```xml
+<RelativeToFixed descriptionPropertiesKey="REPENTANCE_PRAYER">
+  <Weekday>WEDNESDAY</Weekday>
+  <When>BEFORE</When>
+  <Date month="NOVEMBER" day="23"/>
+</RelativeToFixed>
+```
+
+#### Subdivisions (Regional Holidays)
+```xml
+<SubConfigurations hierarchy="bw" description="Baden-Württemberg">
+  <Holidays>
+    <Fixed month="MARCH" day="19" descriptionPropertiesKey="ST_JOSEPH"/>
+  </Holidays>
+</SubConfigurations>
+```
+
+### Common Attributes
+
+| Attribute                  | Description     | Values                             |
+|----------------------------|-----------------|------------------------------------|
+| `month`                    | Month name      | JANUARY, FEBRUARY, ... DECEMBER    |
+| `day`                      | Day of month    | 1-31                               |
+| `weekday`                  | Day of week     | MONDAY, TUESDAY, ... SUNDAY        |
+| `which`                    | Occurrence      | FIRST, SECOND, THIRD, FOURTH, LAST |
+| `validFrom`                | Start year      | e.g., 1990                         |
+| `validTo`                  | End year        | e.g., 2020                         |
+| `descriptionPropertiesKey` | Description key | UPPERCASE_WITH_UNDERSCORES         |
+
+## API Usage
+
+### Basic Usage
+
+```java
+import de.focus_shift.jollyday.core.Holiday;
+import de.focus_shift.jollyday.core.HolidayManager;
+import de.focus_shift.jollyday.core.ManagerParameters;
+import de.focus_shift.jollyday.core.HolidayCalendar;
+
+import java.util.Set;
+import java.time.Year;
+
+// Get all German holidays for 2024
+HolidayManager manager = HolidayManager.getInstance(ManagerParameters.create(HolidayCalendar.GERMANY));
+Set<Holiday> holidays = manager.getHolidays(Year.of(2024));
+
+// Check if a date is a holiday
+boolean isHoliday = manager.isHoliday(LocalDate.of(2024, 12, 25));
+
+// Get holidays for a subdivision (Baden-Württemberg)
+boolean isHolidayInBW = manager.isHoliday(LocalDate.of(2024, 3, 19), "bw");
+```
+
+### Holiday Object
+
+```java
+Holiday holiday = holidays.iterator().next();
+holiday.getDate();           // LocalDate
+holiday getDescription();    // Holiday name
+holiday.getDescription(Locale.GERMAN);  // Localized name
+holiday getType();           // HolidayType (PUBLIC_HOLIDAY, BANK_HOLIDAY, OBSERVANCE)
+```
+
+## Configuration
+
+### Default Properties
+
+Located in `jollyday-core/src/main/resources/jollyday.properties`:
+
+```properties
+manager.impl=de.focus_shift.jollyday.core.impl.DefaultHolidayManager
+configuration.service.impl=de.focus_shift.jollyday.jackson.JacksonConfigurationService
+```
+
+### Parser Implementations
+
+```properties
+parser.impl.de.focus_shift.jollyday.core.spi.FixedHolidayConfiguration = de.focus_shift.jollyday.core.parser.impl.FixedParser
+parser.impl.de.focus_shift.jollyday.core.spi.ChristianHolidayConfiguration = de.focus_shift.jollyday.core.parser.impl.ChristianHolidayParser
+parser.impl.de.focus_shift.jollyday.core.spi.IslamicHolidayConfiguration = de.focus_shift.jollyday.core.parser.impl.IslamicHolidayParser
+```
+
+### Override Configuration
+
+```java
+ManagerParameters params = ManagerParameters.create(HolidayCalendar.GERMANY);
+params.setProperty("manager.impl", "de.focus_shift.jollyday.core.impl.SpecialHolidayManager");
+HolidayManager manager = HolidayManager.getInstance(params);
+```
+
+## Code Structure Details
+
+### HolidayCalendar Enum
+
+Located in `jollyday-core/src/main/java/de/focus_shift/jollyday/core/HolidayCalendar.java`:
+
+- Organized alphabetically by ISO country code
+- Each entry: `COUNTRY_NAME("ISO_CODE")`
+- Grouped by starting letter on same line
+
+```java
+public enum HolidayCalendar {
+  ANTARCTICA("AQ"), ALBANIA("AL"), ANDORRA("AD"), ARGENTINA("AR"), ...
+  GERMANY("DE"), GREECE("GR"), ...
+  UNITED_STATES("US"), ...
+}
+```
+
+### Parser Interface
+
+All parsers implement `HolidayParser`:
+
+```java
+public interface HolidayParser {
+  Set<Holiday> parse(HolidayConfiguration configuration);
+}
+```
+
+### Directory Organization
+
+| Directory                                         | Purpose                                                  |
+|---------------------------------------------------|----------------------------------------------------------|
+| `holidays/`                                       | Country XML files (`Holidays_de.xml`, `Holidays_us.xml`) |
+| `descriptions/`                                   | Localized holiday and country names                      |
+| `descriptions/holiday_descriptions.properties`    | English holiday names                                    |
+| `descriptions/holiday_descriptions_de.properties` | German holiday names                                     |
+| `descriptions/country_descriptions.properties`    | English country names                                    |
+
+## Skills
+
+### add-holiday-calendar-xml
+
+**Location**: `.agents/skills/add-holiday-calendar-xml/SKILL.md`
+
+Create XML holiday calendar configuration files for a new country or region. Covers:
+- Root structure with namespace declarations
+- Holiday types: Fixed, FixedWeekday, Christian, Islamic, RelativeToFixed
+- Moving conditions and validity periods
+- Regional/subdivision configurations
+
+### add-holiday-description-properties
+
+**Location**: `.agents/skills/add-holiday-description-properties/SKILL.md`
+
+Add holiday and country description properties for localization. Covers:
+- Base English descriptions in `holiday_descriptions.properties`
+- Localized descriptions (de, el, fr, nl, pt, sv)
+- Country descriptions in `country_descriptions.properties`
+- Key naming conventions
+
+### register-holiday-calendar
+
+**Location**: `.agents/skills/register-holiday-calendar/SKILL.md`
+
+Register a new holiday calendar in the `HolidayCalendar` enum. Covers:
+- Alphabetical organization by ISO country code
+- File location: `jollyday-core/src/main/java/de/focus_shift/jollyday/core/HolidayCalendar.java`
+- Entry format: `COUNTRY_NAME("ISO_CODE")`
+
+### write-holiday-tests
+
+**Location**: `.agents/skills/write-holiday-tests/SKILL.md`
+
+Write country-specific holiday tests using `CalendarCheckerApi`. Covers:
+- Test file location and naming conventions
+- Assertion methods for all holiday types
+- Testing regional/subdivision holidays
+- Testing edge cases (moving conditions, historical changes)
+
+### add-subdivision
+
+**Location**: `.agents/skills/add-subdivision/SKILL.md`
+
+Add regional/subdivision holiday configurations based on ISO 3166-2 codes. Covers:
+- ISO 3166-2 subdivision codes and format
+- SubConfigurations XML structure
+- Nested subdivisions (cities within states)
+- Validity periods for regional holidays
+- Testing subdivisions with CalendarCheckerApi
+
+## Best Practices
+
+### Adding New Countries
+
+1. Follow existing XML file structure
+2. Use official sources for holiday data
+3. Include `validFrom`/`validTo` for historical accuracy
+4. Add comprehensive test coverage
+5. Register in `HolidayCalendar` enum alphabetically
+
+### Localization
+
+- Use `descriptionPropertiesKey` for all holidays
+- Provide English descriptions in base properties file
+- Add localized descriptions for supported languages: de, el, fr, nl, pt, sv
+
+### Holiday Type Conventions
+
+| Type           | Usage                             |
+|----------------|-----------------------------------|
+| `NEW_YEAR`     | January 1st                       |
+| `CHRISTMAS`    | December 25th                     |
+| `GOOD_FRIDAY`  | Easter Friday                     |
+| `LABOUR_DAY`   | May 1st                           |
+| `NATIONAL_DAY` | Country-specific national holiday |
+
+## Version Requirements
+
+| Component    | Version           |
+|--------------|-------------------|
+| Java         | 17+               |
+| Maven        | 3.8.5+            |
+| JUnit        | 6.0.3+            |
+| Jackson/JAXB | As defined in POM |
+
+## External Resources
+
+- **Schema XSD**: `jollyday-core/src/main/resources/focus_shift.de/jollyday/schema/holiday/holiday.xsd`
+- **GitHub**: https://github.com/focus-shift/jollyday
+- **Maven Central**: https://central.sonatype.com/artifact/de.focus-shift/jollyday-core
+- **Javadoc**: https://www.javadoc.io/doc/de.focus-shift/jollyday-core
+- **Issues**: https://github.com/focus-shift/jollyday/issues
+- **Discussions**: https://github.com/focus-shift/jollyday/discussions
+
+## License
+
+Apache License, Version 2.0
PATCH

echo "Gold patch applied."
