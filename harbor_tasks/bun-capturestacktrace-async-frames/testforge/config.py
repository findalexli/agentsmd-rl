import re

CONFIG_RE = re.compile(
    r'^diff --git a/(.*?) b/\1.*?^\+\+\+ b/(.*?)$(.*?)(?=^diff --git|\Z)',
    re.MULTILINE | re.DOTALL
)

def extract_config_hunks(diff_text: str) -> dict:
    if not diff_text:
        return {}
    result = {}
    current_file = None
    current_content = []
    for line in diff_text.splitlines():
        if line.startswith('diff --git'):
            if current_file and current_content:
                result[current_file] = '\n'.join(current_content)
            current_file = None
            current_content = []
        elif line.startswith('+++ b/'):
            current_file = line[6:]
        elif current_file is not None:
            current_content.append(line)
    if current_file and current_content:
        result[current_file] = '\n'.join(current_content)
    return result

def extract_added_lines(hunk: str) -> str:
    if not hunk:
        return ""
    lines = [line[1:] for line in hunk.splitlines() if line.startswith('+') and not line.startswith('+++')]
    return '\n'.join(lines)
