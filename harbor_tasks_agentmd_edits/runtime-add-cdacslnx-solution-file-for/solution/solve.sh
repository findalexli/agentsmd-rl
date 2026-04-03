#!/usr/bin/env bash
set -euo pipefail

cd /workspace/runtime

# Idempotent: skip if already applied
if [ -f src/native/managed/cdac/cdac.slnx ]; then
    echo "Patch already applied."
    exit 0
fi

# Create the cdac.slnx solution file
cat > src/native/managed/cdac/cdac.slnx <<'SLNX'
<Solution>
  <Configurations>
    <Platform Name="Any CPU" />
    <Platform Name="x64" />
    <Platform Name="x86" />
  </Configurations>
  <Folder Name="/cdac/">
    <Project Path="Microsoft.Diagnostics.DataContractReader.Abstractions/Microsoft.Diagnostics.DataContractReader.Abstractions.csproj" />
    <Project Path="Microsoft.Diagnostics.DataContractReader.Contracts/Microsoft.Diagnostics.DataContractReader.Contracts.csproj" />
    <Project Path="Microsoft.Diagnostics.DataContractReader/Microsoft.Diagnostics.DataContractReader.csproj" />
    <Project Path="Microsoft.Diagnostics.DataContractReader.Legacy/Microsoft.Diagnostics.DataContractReader.Legacy.csproj" />
    <Project Path="mscordaccore_universal/mscordaccore_universal.csproj" />
  </Folder>
  <Folder Name="/tests/">
    <Project Path="tests/Microsoft.Diagnostics.DataContractReader.Tests.csproj" />
    <Project Path="tests/DumpTests/Microsoft.Diagnostics.DataContractReader.DumpTests.csproj" />
  </Folder>
</Solution>
SLNX

# Update README.md — replace the manual "Setting up a solution" section
# with an "Opening the solution" section referencing the checked-in file
python3 -c "
import re
p = 'src/native/managed/cdac/README.md'
with open(p) as f:
    content = f.read()

old_section = re.search(
    r'### Setting up a solution.*?(?=### Running unit tests)',
    content,
    re.DOTALL
)
if old_section:
    new_section = '''### Opening the solution

The [\`cdac.slnx\`](cdac.slnx) solution file in this directory brings all cDAC projects and
tests into scope. In VS Code, run the \".NET: Open Solution\" command and select
\\\`src/native/managed/cdac/cdac.slnx\\\`. In Visual Studio, open the file directly. You can then
use Test Explorer to run and debug tests.

'''
    content = content[:old_section.start()] + new_section + content[old_section.end():]
    with open(p, 'w') as f:
        f.write(content)
"

echo "Patch applied successfully."
