import fs from 'fs';
const src = fs.readFileSync(
    'compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts',
    'utf-8'
);
const panStart = src.indexOf("PanResponder:");
const freezeIdx = src.indexOf("kind: 'Freeze'", panStart);
const immutableIdx = src.indexOf("kind: 'ImmutableCapture'", panStart);
console.log("PanResponder at:", panStart);
console.log("Freeze at:", freezeIdx, "distance:", freezeIdx - panStart);
console.log("ImmutableCapture at:", immutableIdx, "distance:", immutableIdx - panStart);
console.log("\n1000-char block excerpt (end):");
console.log(src.slice(panStart + 900, panStart + 1000));
