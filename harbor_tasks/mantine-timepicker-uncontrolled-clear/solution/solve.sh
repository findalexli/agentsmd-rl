#!/bin/bash
set -e

cd /workspace/mantine_repo

# Write Python script to apply the fix
python3 << 'ENDPY'
import re

# Fix use-time-picker.ts
with open('packages/@mantine/dates/src/components/TimePicker/use-time-picker.ts', 'r') as f:
    content = f.read()

# Add initialTimeString before acceptChange ref
old1 = '''  const acceptChange = useRef(true);'''
new1 = '''  const initialTimeString = getTimeString({
    hours: parsedTime.hours,
    minutes: parsedTime.minutes,
    seconds: parsedTime.seconds,
    format,
    withSeconds,
    amPm: parsedTime.amPm,
    amPmLabels,
  });

  const acceptChange = useRef(true);
  const wasInvalidBefore = useRef(!initialTimeString.valid);'''
content = content.replace(old1, new1)

# Set wasInvalidBefore.current = false when valid
old2 = '''    if (timeString.valid) {
      acceptChange.current = false;
      if (field === 'hours') {'''
new2 = '''    if (timeString.valid) {
      acceptChange.current = false;
      wasInvalidBefore.current = false;
      if (field === 'hours') {'''
content = content.replace(old2, new2)

# Change the value check to wasInvalidBefore check
old3 = '''    } else {
      acceptChange.current = false;
      if (typeof value === 'string' && value !== '') {
        onChange?.('');
      }
    }'''
new3 = '''    } else {
      acceptChange.current = false;
      if (!wasInvalidBefore.current) {
        onChange?.('');
        wasInvalidBefore.current = true;
      }
    }'''
content = content.replace(old3, new3)

# Add wasInvalidBefore update in setTimeString
old4 = '''  const setTimeString = (timeString: string) => {
    acceptChange.current = false;

    const parsedTime = getParsedTime({ time: timeString, amPmLabels, format });
    setHours(parsedTime.hours);
    setMinutes(parsedTime.minutes);
    setSeconds(parsedTime.seconds);
    setAmPm(parsedTime.amPm);

    onChange?.(timeString);
  };'''
new4 = '''  const setTimeString = (timeString: string) => {
    acceptChange.current = false;

    const parsedTime = getParsedTime({ time: timeString, amPmLabels, format });
    setHours(parsedTime.hours);
    setMinutes(parsedTime.minutes);
    setSeconds(parsedTime.seconds);
    setAmPm(parsedTime.amPm);

    const next = getTimeString({ ...parsedTime, format, withSeconds, amPmLabels });
    wasInvalidBefore.current = !next.valid;
    onChange?.(timeString);
  };'''
content = content.replace(old4, new4)

# Add wasInvalidBefore.current = true in clear()
old5 = '''  const clear = () => {
    acceptChange.current = false;
    setHours(null);
    setMinutes(null);
    setSeconds(null);
    setAmPm(null);
    onChange?.('');
    focus('hours');
  };'''
new5 = '''  const clear = () => {
    acceptChange.current = false;
    setHours(null);
    setMinutes(null);
    setSeconds(null);
    setAmPm(null);
    onChange?.('');
    wasInvalidBefore.current = true;
    focus('hours');
  };'''
content = content.replace(old5, new5)

with open('packages/@mantine/dates/src/components/TimePicker/use-time-picker.ts', 'w') as f:
    f.write(content)

print("use-time-picker.ts updated")

# Fix TimePicker.test.tsx - add new test before "handles left/right arrow keys correctly"
with open('packages/@mantine/dates/src/components/TimePicker/TimePicker.test.tsx', 'r') as f:
    content = f.read()

new_test = '''  it('calls onChange when cleared with backspace in uncontrolled mode', async () => {
    const spy = jest.fn();
    render(<TimePicker {...defaultProps} defaultValue="12:34" onChange={spy} />);

    await userEvent.click(screen.getByLabelText('test-hours'));
    await userEvent.type(document.activeElement!, '{backspace}');

    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenLastCalledWith('');
  });
'''
old_test = '''  it('handles left/right arrow keys correctly', async () => {
    render(<TimePicker {...defaultProps} withSeconds format="24h" />);'''

content = content.replace(old_test, new_test + old_test)

with open('packages/@mantine/dates/src/components/TimePicker/TimePicker.test.tsx', 'w') as f:
    f.write(content)

print("TimePicker.test.tsx updated")
ENDPY

grep -q "wasInvalidBefore" packages/@mantine/dates/src/components/TimePicker/use-time-picker.ts