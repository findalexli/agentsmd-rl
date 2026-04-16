#!/bin/bash
set -e

cd /workspace/dagster

# Apply the timezone optimization patch
cat <<'PATCH' | git apply -
diff --git a/python_modules/dagster/dagster/_utils/schedules.py b/python_modules/dagster/dagster/_utils/schedules.py
index a5c57ba734b17..6222919d9dc99 100644
--- a/python_modules/dagster/dagster/_utils/schedules.py
+++ b/python_modules/dagster/dagster/_utils/schedules.py
@@ -35,6 +35,12 @@ def expand(cls, *args, **kwargs):  # pyright: ignore[reportIncompatibleMethodOve
         return super().expand(*args, **kwargs)


+@functools.cache
+def has_nonzero_minute_offset(tz_str: str) -> bool:
+    offset = datetime.datetime.now(get_timezone(tz_str)).utcoffset()
+    return offset is not None and (offset.total_seconds() % 3600) != 0
+
+
 def _is_simple_cron(
     cron_expression: str,
     dt: datetime.datetime,
@@ -148,6 +154,7 @@ def _find_hourly_schedule_time(
     date: datetime.datetime,
     ascending: bool,
     already_on_boundary: bool,
+    use_timezone_minute_resolution: bool,
 ) -> datetime.datetime:
     if ascending:
         # short-circuit if minutes and seconds are already correct
@@ -168,7 +175,11 @@ def _find_hourly_schedule_time(
             + (SECONDS_PER_MINUTE - new_timestamp % SECONDS_PER_MINUTE) % SECONDS_PER_MINUTE
         )

-        current_minute = datetime.datetime.fromtimestamp(new_timestamp, tz=date.tzinfo).minute
+        current_minute = (
+            datetime.datetime.fromtimestamp(new_timestamp, tz=date.tzinfo).minute
+            if use_timezone_minute_resolution
+            else (new_timestamp // SECONDS_PER_MINUTE) % MINUTES_PER_HOUR
+        )

         final_timestamp = None

@@ -202,7 +213,11 @@ def _find_hourly_schedule_time(
         new_timestamp = new_timestamp - new_timestamp % SECONDS_PER_MINUTE

         # move minutes back to correct place
-        current_minute = datetime.datetime.fromtimestamp(new_timestamp, tz=date.tzinfo).minute
+        current_minute = (
+            datetime.datetime.fromtimestamp(new_timestamp, tz=date.tzinfo).minute
+            if use_timezone_minute_resolution
+            else (new_timestamp // SECONDS_PER_MINUTE) % MINUTES_PER_HOUR
+        )

         final_timestamp = None

@@ -382,12 +397,17 @@ def _find_schedule_time(
     # lets us skip slow work to find the starting point if we know that
     # we are already on the boundary of the cron interval
     already_on_boundary: bool,
+    use_timezone_minute_resolution: bool = False,
 ) -> datetime.datetime:
     from dagster._core.definitions.partitions.schedule_type import ScheduleType

     if schedule_type == ScheduleType.HOURLY:
         return _find_hourly_schedule_time(
-            check.not_none(minutes), date, ascending, already_on_boundary
+            check.not_none(minutes),
+            date,
+            ascending,
+            already_on_boundary,
+            use_timezone_minute_resolution,
         )
     elif schedule_type == ScheduleType.DAILY:
         minutes = check.not_none(minutes)
@@ -723,6 +743,11 @@ def cron_string_iterator(
         expected_days_of_week = cron_parts[4]

     if known_schedule_type:
+        use_timezone_minute_resolution = (
+            known_schedule_type == ScheduleType.HOURLY
+            and execution_timezone is not None
+            and has_nonzero_minute_offset(execution_timezone)
+        )
         start_datetime = datetime.datetime.fromtimestamp(
             start_timestamp, tz=get_timezone(execution_timezone)
         )
@@ -743,6 +768,7 @@ def cron_string_iterator(
                 start_datetime,
                 ascending=not ascending,  # Going in the reverse direction
                 already_on_boundary=False,
+                use_timezone_minute_resolution=use_timezone_minute_resolution,
             )
             check.invariant(start_offset <= 0)
             for _ in range(-start_offset):
@@ -755,6 +781,7 @@ def cron_string_iterator(
                     next_date,
                     ascending=not ascending,  # Going in the reverse direction
                     already_on_boundary=True,
+                    use_timezone_minute_resolution=use_timezone_minute_resolution,
                 )

         while True:
@@ -767,6 +794,7 @@ def cron_string_iterator(
                 next_date,
                 ascending=ascending,
                 already_on_boundary=True,
+                use_timezone_minute_resolution=use_timezone_minute_resolution,
             )

             if start_offset == 0:
PATCH

# Idempotency check - verify the new function exists
grep -q "def has_nonzero_minute_offset" python_modules/dagster/dagster/_utils/schedules.py && \
    echo "Patch applied successfully" || \
    (echo "Patch failed to apply" && exit 1)
