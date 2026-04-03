#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if [ -f tests/assets/webfont/generate_font.py ]; then
    echo "Patch already applied."
    exit 0
fi

# 1. Create the font generation script
cat > tests/assets/webfont/generate_font.py <<'PYSCRIPT'
#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Generate iconfont.woff2 with simple rectangle glyphs for + (U+2B) and - (U+2D).

Requirements: pip3 install fonttools brotli
"""

import os

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen

fb = FontBuilder(1000, isTTF=False)
fb.setupGlyphOrder([".notdef", "plus", "hyphen"])
fb.setupCharacterMap({0x2B: "plus", 0x2D: "hyphen"})

fb.setupHorizontalMetrics({
    ".notdef": (1000, 0),
    "plus": (1000, 100),
    "hyphen": (1000, 100),
})
fb.setupHorizontalHeader(ascent=850, descent=-150)
fb.setupNameTable({
    "familyName": "pwtest-iconfont",
    "styleName": "Regular",
})
fb.setupOS2(sTypoAscender=850, sTypoDescender=-150, sTypoLineGap=0,
            usWinAscent=850, usWinDescent=150)
fb.setupPost()

charstrings = {}
pen = T2CharStringPen(1000, None)
charstrings[".notdef"] = pen.getCharString()

for name in ["plus", "hyphen"]:
    pen = T2CharStringPen(1000, None)
    pen.moveTo((100, 0))
    pen.lineTo((900, 0))
    pen.lineTo((900, 700))
    pen.lineTo((100, 700))
    pen.closePath()
    charstrings[name] = pen.getCharString()

fb.setupCFF(
    psName="pwtest-iconfont",
    fontInfo={"version": "1.0"},
    charStringsDict=charstrings,
    privateDict={}
)

fb.font.flavor = "woff2"
output_path = os.path.join(os.path.dirname(__file__), "iconfont.woff2")
fb.font.save(output_path)
print(f"Saved {output_path}")
PYSCRIPT

chmod +x tests/assets/webfont/generate_font.py

# 2. Update the SVG with simplified rectangle glyphs
sed -i 's|<glyph glyph-name="plus" unicode="&#x2b;" d="M531 527a31 31 0 0 1-62 0v-146h-146a31 31 0 0 1 0-62h146v-146a31 31 0 0 1 62 0v146h146a31 31 0 0 1 0 62h-146v146z m-31 281c-253 0-458-205-458-458s205-458 458-458 458 205 458 458-205 458-458 458z m-396-458a396 396 0 1 0 792 0 396 396 0 0 0-792 0z" horiz-adv-x="1000" />|<glyph glyph-name="plus" unicode="\&#x2b;" d="M100 0h800v700h-800z" horiz-adv-x="1000" />|' tests/assets/webfont/iconfont.svg

sed -i 's|<glyph glyph-name="minus" unicode="&#x2d;" d="M104 350a396 396 0 1 0 792 0 396 396 0 0 0-792 0z m396 458c-253 0-458-205-458-458s205-458 458-458 458 205 458 458-205 458-458 458z m260-489a31 31 0 0 1 0 62h-520a31 31 0 0 1 0-62h520z" horiz-adv-x="1000" />|<glyph glyph-name="minus" unicode="\&#x2d;" d="M100 0h800v700h-800z" horiz-adv-x="1000" />|' tests/assets/webfont/iconfont.svg

# 3. Update the README
cat > tests/assets/webfont/README.md <<'README'
This font contains two glyphs — `+` (U+2B) and `-` (U+2D) — each rendered as a
simple filled black rectangle. The simplicity makes screenshot tests insensitive
to font-rendering/antialiasing differences across platforms.

## Regenerating

Install dependencies:

```
pip3 install fonttools brotli
```

Run `generate_font.py` to regenerate `iconfont.woff2`:

```
python3 tests/assets/webfont/generate_font.py
```
README

# 4. Regenerate the woff2 font
python3 tests/assets/webfont/generate_font.py

# 5. Copy regenerated font to ct-react-vite assets
cp tests/assets/webfont/iconfont.woff2 tests/components/ct-react-vite/src/assets/iconfont.woff2

# 6. Update body.length expectations in route.spec.tsx
sed -i 's/expect(body\.length)\.toBe(2656)/expect(body.length).toBe(348)/g' tests/components/ct-react-vite/tests/route.spec.tsx

echo "Patch applied successfully."
