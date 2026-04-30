import pathlib
f = pathlib.Path('/tests/test_outputs.py')
t = f.read_text()

bad1 = "r'NEXT_RUNTIME\\s*===\\s*[\\'\\\"]edge[\\'\\\"]\\''"
good1 = "r\"NEXT_RUNTIME\\s*===\\s*['\\\"]edge['\\\"]\""
t = t.replace(bad1, good1)

bad2 = "r'require\\([\\'\"]node:stream[\\'']\\)\""
good2 = "r\"require\\(['\\\"]node:stream['\\\"]\\)\""
t = t.replace(bad2, good2)

f.write_text(t)
