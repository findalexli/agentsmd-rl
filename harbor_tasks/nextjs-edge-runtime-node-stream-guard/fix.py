import pathlib
f = pathlib.Path('/tests/test_outputs.py')
t = f.read_text()
t = t.replace("r'NEXT_RUNTIME\\s*===\\s*['\"]edge['\"]'", "r'NEXT_RUNTIME\\s*===\\s*[\\'\\\"]edge[\\'\\\"]\\''")
f.write_text(t)
