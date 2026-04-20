import subprocess
import os
import tempfile

# Write the bundle script to disk
bundle_script = '''
const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

esbuild.build({
  entryPoints: ['/workspace/mantine/packages/@mantine/mcp-server/src/server.ts'],
  bundle: true,
  platform: 'node',
  outfile: '/workspace/mantine/server_bundle.cjs',
  format: 'cjs',
  sourcemap: false,
  minify: false,
  external: ['./data-client', './types'],
  loader: { '.ts': 'ts' }
}).then(() => {
  console.log('BUNDLED OK');
}).catch(err => {
  console.error('ERROR:', err.message);
  process.exit(1);
});
'''

with open('/workspace/mantine/bundle_esbuild.js', 'w') as f:
    f.write(bundle_script)

# Run the bundle script
result = subprocess.run(['node', '/workspace/mantine/bundle_esbuild.js'],
    cwd='/workspace/mantine', capture_output=True, text=True, timeout=30)
print('BUNDLE STDOUT:', result.stdout)
print('BUNDLE STDERR:', result.stderr[:200])
print('BUNDLE RC:', result.returncode)

# Clean up bundle script
try:
    os.unlink('/workspace/mantine/bundle_esbuild.js')
except:
    pass

# Check if bundle exists
bundle_path = '/workspace/mantine/server_bundle.cjs'
if os.path.exists(bundle_path):
    print('BUNDLE EXISTS, SIZE:', os.path.getsize(bundle_path))
else:
    print('BUNDLE NOT FOUND')