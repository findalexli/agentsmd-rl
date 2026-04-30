import pathlib, re
f = pathlib.Path('/tests/test_outputs.py')
t = f.read_text()
def repl(m):
    inner = m.group(1).replace("'", "\\'")
    return "r'" + inner + "'"
t = re.sub(r'r"([^"]*\[\x27"\][^"]*)"', repl, t)
f.write_text(t)
