#!/bin/bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if ! grep -q 'SetupSccache' CMakeLists.txt 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

echo "Applying CMakeLists.txt changes..."
python3 << 'PYEOF'
import re

with open('CMakeLists.txt', 'r') as f:
    content = f.read()

old_block = '''find_program(SCCACHE_PROGRAM sccache)
if(SCCACHE_PROGRAM AND NOT DEFINED ENV{NO_SCCACHE})
  include(SetupSccache)
else()
  find_program(CCACHE_PROGRAM ccache)
  if(CCACHE_PROGRAM)
    include(SetupCcache)
  endif()
endif()'''

new_block = 'include(SetupCcache)'

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('CMakeLists.txt', 'w') as f:
        f.write(content)
    print("CMakeLists.txt updated")
else:
    print("WARNING: Could not find SCCACHE block")
PYEOF

echo "Applying SetupCcache.cmake changes..."
python3 << 'PYEOF'
import re

with open('cmake/tools/SetupCcache.cmake', 'r') as f:
    content = f.read()

# Remove the CI/CCACHE_DISABLE block - more flexible regex
# Match the entire block including the trailing newlines
pattern = r'if \(CI AND NOT APPLE\)\s*\n\s*setenv\(CCACHE_DISABLE 1\)\s*\n\s*return\(\)\s*\n\s*endif\(\)\s*\n*'
content = re.sub(pattern, '\n', content)
print("Removed CI block")

# Remove REQUIRED and ${CI} from find_command
pattern = r'(find_command\(\s*\n\s*VARIABLE\s*\n\s*CCACHE_PROGRAM\s*\n\s*COMMAND\s*\n\s*ccache)\s*\n\s*REQUIRED\s*\n\s*\$\{CI\}\s*\n\s*(\))'
content = re.sub(pattern, r'\1\n\2', content)
print("Removed REQUIRED from find_command")

with open('cmake/tools/SetupCcache.cmake', 'w') as f:
    f.write(content)
PYEOF

rm -f cmake/tools/SetupSccache.cmake

echo "Applying bootstrap.sh changes..."
python3 << 'PYEOF'
import re

with open('scripts/bootstrap.sh', 'r') as f:
    content = f.read()

content = content.replace('# Version: 25', '# Version: 26')
content = content.replace('install_sccache', 'install_ccache')

old_func_start = 'install_ccache() {'
func_start_idx = content.find(old_func_start)
if func_start_idx != -1:
    brace_count = 0
    func_end_idx = func_start_idx
    in_function = False
    for i in range(func_start_idx, len(content)):
        if content[i] == '{':
            brace_count += 1
            in_function = True
        elif content[i] == '}':
            brace_count -= 1
            if in_function and brace_count == 0:
                func_end_idx = i + 1
                break
    
    old_func = content[func_start_idx:func_end_idx]
    new_func = '''install_ccache() {
\tcase "$pm" in
\tapt|brew|apk|dnf|yum|zypper)
\t\tinstall_packages ccache
\t\t;;
\tesac
}'''
    content = content.replace(old_func, new_func)
    print("Replaced install_ccache function")

content = content.replace(
    '# checkout directory. sccache hashes absolute paths into its cache keys,',
    '# checkout directory for ccache to be effective.'
)
content = re.sub(r'# so if buildkite uses a different checkout path each time \(which it does\n', '', content)
content = re.sub(r'# by default\), sccache will be useless\.\n', '', content)

with open('scripts/bootstrap.sh', 'w') as f:
    f.write(content)
print("bootstrap.sh updated")
PYEOF

echo "Removing scripts/build-cache directory..."
rm -rf scripts/build-cache

echo "Applying build.mjs changes..."
python3 << 'PYEOF'
try:
    with open('scripts/build.mjs', 'r') as f:
        content = f.read()
    content = content.replace('sccache', 'ccache')
    content = content.replace('Sccache', 'Ccache')
    with open('scripts/build.mjs', 'w') as f:
        f.write(content)
    print("build.mjs updated")
except FileNotFoundError:
    print("build.mjs not found")
PYEOF

echo "Applying CONTRIBUTING.md changes..."
python3 << 'PYEOF'
import re

with open('CONTRIBUTING.md', 'r') as f:
    content = f.read()

# Update brew install line
content = content.replace(
    'brew install automake cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby sccache',
    'brew install automake ccache cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby'
)

# Replace section header
content = content.replace('### Optional: Install `sccache`', '### Optional: Install `ccache`')

# Replace description line
content = content.replace(
    'sccache is used to cache compilation artifacts, significantly speeding up builds. It must be installed with S3 support:',
    'ccache is used to cache compilation artifacts, significantly speeding up builds:'
)

# Replace brew install command in code block
content = content.replace('$ brew install sccache', '$ brew install ccache')

# Remove Linux cargo install line
content = re.sub(
    r'# For Linux\. Note that the version in your package manager may not have S3 support\.\n\$ cargo install sccache --features=s3\n',
    '',
    content
)

# Remove sccache explanation text
content = re.sub(
    r'This will install `sccache` with S3 support[^*]*\*\*Note\*\*: Not all versions of `sccache` are compiled with S3 support, hence we recommend installing it via `cargo`\.\n\n',
    '',
    content
)

# Remove entire AWS credentials section - more flexible pattern
# Match from the header through the paragraph about AWS credentials
content = re.sub(
    r'#### Registering AWS Credentials for `sccache` \(Core Developers Only\)[^#]*?'
    r'The `cmake` scripts should automatically detect your AWS credentials[^\n]*\n\n',
    '',
    content,
    flags=re.DOTALL
)

# Remove AWS CLI details section - match everything between <details> and </details>
content = re.sub(
    r'<details>\s*<summary>Logging in to the `aws` CLI</summary>.*?</details>\s*',
    '',
    content,
    flags=re.DOTALL
)

# Remove Common Issues section
content = re.sub(
    r'<details>\s*<summary>Common Issues You May Encounter</summary>.*?</details>\s*',
    '''```

For other platforms:
```bash
# For Ubuntu/Debian
$ sudo apt install ccache

# For Arch
$ sudo pacman -S ccache

# For Fedora
$ sudo dnf install ccache

# For openSUSE
$ sudo zypper install ccache
```

Our build scripts will automatically detect and use `ccache` if available. You can check cache statistics with `ccache --show-stats`.

''',
    content,
    flags=re.DOTALL
)

with open('CONTRIBUTING.md', 'w') as f:
    f.write(content)
print("CONTRIBUTING.md updated")
PYEOF

echo "Applying docs/project/contributing.mdx changes..."
python3 << 'PYEOF'
import re

with open('docs/project/contributing.mdx', 'r') as f:
    content = f.read()

# Update brew install line
content = content.replace(
    'brew install automake cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby sccache',
    'brew install automake ccache cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby'
)

# Replace section header
content = content.replace('### Optional: Install `sccache`', '### Optional: Install `ccache`')

# Replace description
content = content.replace(
    'sccache is used to cache compilation artifacts, significantly speeding up builds. It must be installed with S3 support:',
    'ccache is used to cache compilation artifacts, significantly speeding up builds:'
)

# Replace brew install command
content = content.replace('$ brew install sccache', '$ brew install ccache')

# Remove Linux cargo install
content = re.sub(
    r'# For Linux\. Note that the version in your package manager may not have S3 support\.\n\$ cargo install sccache --features=s3\n',
    '',
    content
)

# Remove sccache explanation
content = re.sub(
    r'This will install `sccache` with S3 support[^*]*\*\*Note\*\*: Not all versions of `sccache` are compiled with S3 support[^\n]*\n',
    '',
    content
)

# Remove AWS credentials section - more flexible
content = re.sub(
    r'#### Registering AWS Credentials for `sccache` \(Core Developers Only\)[^#]*?'
    r'The `cmake` scripts should automatically detect your AWS credentials[^\n]*\n\n',
    '',
    content,
    flags=re.DOTALL
)

# Remove AWS CLI details
content = re.sub(
    r'<details>\s*<summary>Logging in to the `aws` CLI</summary>.*?</details>\s*',
    '',
    content,
    flags=re.DOTALL
)

# Remove Common Issues section and replace with ccache info
content = re.sub(
    r'<details>\s*<summary>Common Issues You May Encounter</summary>.*?</details>',
    '''```

For other platforms:
```bash
# For Ubuntu/Debian
$ sudo apt install ccache

# For Arch
$ sudo pacman -S ccache

# For Fedora
$ sudo dnf install ccache

# For openSUSE
$ sudo zypper install ccache
```

Our build scripts will automatically detect and use `ccache` if available. You can check cache statistics with `ccache --show-stats`.''',
    content,
    flags=re.DOTALL
)

with open('docs/project/contributing.mdx', 'w') as f:
    f.write(content)
print("contributing.mdx updated")
PYEOF

echo "Applying docs/project/building-windows.mdx changes..."
python3 << 'PYEOF'
with open('docs/project/building-windows.mdx', 'r') as f:
    content = f.read()

content = content.replace('sccache', 'ccache')

with open('docs/project/building-windows.mdx', 'w') as f:
    f.write(content)
print("building-windows.mdx updated")
PYEOF

echo "All changes applied."
