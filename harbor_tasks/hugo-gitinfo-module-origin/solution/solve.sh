#!/bin/bash
set -e

cd /workspace/hugo

# Check if already applied (idempotency)
if grep -q 'func (o ModuleOrigin) IsZero()' modules/module.go 2>/dev/null; then
    echo 'Patch already applied, skipping'
    exit 0
fi

echo 'Applying changes...'

# Fix 1: hugolib/gitinfo.go - Add IsZero() check
python3 << 'PYEOF'
with open('hugolib/gitinfo.go', 'r') as f:
    content = f.read()

old = 'if mod.Owner() == nil {'
new = 'if mod.Owner() == nil && !mod.Origin().IsZero() {'
content = content.replace(old, new)

with open('hugolib/gitinfo.go', 'w') as f:
    f.write(content)
print('Fixed hugolib/gitinfo.go')
PYEOF

# Fix 2: Rename test function
python3 << 'PYEOF'
with open('hugolib/gitinfo_github_test.go', 'r') as f:
    content = f.read()
content = content.replace('func TestGitInfoFromGitModule(', 'func TestGitInfoFromGitModuleWithVersionQuery(')
with open('hugolib/gitinfo_github_test.go', 'w') as f:
    f.write(content)
print('Fixed gitinfo_github_test.go')
PYEOF

# Fix 3: hugo_sites.go - return error instead of logging
python3 << 'PYEOF'
with open('hugolib/hugo_sites.go', 'r') as f:
    content = f.read()
content = content.replace('h.Log.Errorln("Failed to read Git log:", err)', 'return err')
with open('hugolib/hugo_sites.go', 'w') as f:
    f.write(content)
print('Fixed hugo_sites.go')
PYEOF

# Fix 4: modules/module.go - Add IsZero() method
python3 << 'PYEOF'
with open('modules/module.go', 'r') as f:
    content = f.read()

struct_end = '''type ModuleOrigin struct {
\tVCS  string // version control system, e.g. "git"
\tURL  string // repository URL, e.g. "https://github.com/bep/hugo-testing-git-versions"
\tHash string // commit hash
\tRef  string // e.g. "refs/tags/v3.0.1"
}'''

new_struct = '''type ModuleOrigin struct {
\tVCS  string // version control system, e.g. "git"
\tURL  string // repository URL, e.g. "https://github.com/bep/hugo-testing-git-versions"
\tHash string // commit hash
\tRef  string // e.g. "refs/tags/v3.0.1"
}

func (o ModuleOrigin) IsZero() bool {
\treturn o.URL == ""
}'''

content = content.replace(struct_end, new_struct)

with open('modules/module.go', 'w') as f:
    f.write(content)
print('Fixed module.go')
PYEOF

# Fix 5: modules/client.go - Add nil Origin handling
python3 << 'PYEOF'
with open('modules/client.go', 'r') as f:
    content = f.read()

old_pattern = '''\tfor _, m := range modules {
\t\tif m.Dir == "" {
\t\t\tmodulesToDownload = append(modulesToDownload, fmt.Sprintf("%s@%s", m.Path, m.Version))
\t\t}
\t}'''

new_pattern = '''\tfor _, m := range modules {
\t\tif m.Dir == "" {
\t\t\tmodulesToDownload = append(modulesToDownload, fmt.Sprintf("%s@%s", m.Path, m.Version))
\t\t}

\t\t// See https://github.com/golang/go/issues/67363
\t\t// Origin isn\'t always set.
\t\tif m.Origin == nil && m.GoMod != "" {
\t\t\t// There\'s sometimes an Info field with a JSON filename with this info, but that is also not always set.
\t\t\t// But we seem to always get the go.mod filename, so we can determine the info filename from that,
\t\t\t// just replace the .mod suffix with .info.
\t\t\tinfoFilename := strings.TrimSuffix(m.GoMod, ".mod") + ".info"
\t\t\t// JSON on the form {"Version":"v0.0.0-20260225095909-668663b54d09","Time":"2026-02-25T09:59:09Z","Origin":{"VCS":"git","URL":"https://github.com/bep/hugo-mod-testing-content","Hash":"668663b54d0937df05185d144765d13c3ffda489"}}
\t\t\tif b, err := afero.ReadFile(c.fs, infoFilename); err == nil {
\t\t\t\tvar info struct {
\t\t\t\t\tVersion string
\t\t\t\t\tTime    time.Time
\t\t\t\t\tOrigin  *goModuleOrigin
\t\t\t\t}
\t\t\t\tif err := json.Unmarshal(b, &info); err == nil {
\t\t\t\t\tm.Origin = info.Origin
\t\t\t\t}
\t\t\t}
\t\t}
\t}'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open('modules/client.go', 'w') as f:
        f.write(content)
    print('Fixed client.go')
else:
    print('ERROR: Could not find insertion pattern in client.go')
    exit(1)
PYEOF

echo 'All changes applied successfully'
