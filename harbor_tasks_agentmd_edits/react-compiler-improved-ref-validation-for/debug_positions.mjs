import fs from 'fs';
const src = fs.readFileSync(
    'compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts',
    'utf-8'
);

const immutableIdx = src.indexOf("case 'ImmutableCapture':");
const freezeIdx = src.indexOf("e.kind === 'Freeze'", immutableIdx);
const idIdx = src.indexOf("identifier.id", immutableIdx);

console.log("ImmutableCapture at: ", immutableIdx);
console.log("e.kind === 'Freeze' at: ", freezeIdx);
console.log("identifier.id at: ", idIdx);
console.log("Distance to Freeze: ", freezeIdx - immutableIdx);
console.log("Distance to id: ", idIdx - immutableIdx);
