import fs from 'fs';

// Test 1: ImmutableCapture case
const src = fs.readFileSync(
    'compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts',
    'utf-8'
);

// Must handle ImmutableCapture effect kind in the effects switch
if (!src.includes("case 'ImmutableCapture':")) {
    console.log('FAIL: Missing ImmutableCapture case');
} else {
    console.log('PASS: Has ImmutableCapture case');
}

// ImmutableCapture handler must check for co-occurring Freeze effect on same operand
const immutableIdx = src.indexOf("case 'ImmutableCapture':");
const nearbyCode = src.slice(immutableIdx, immutableIdx + 600);

console.log('ImmutableCapture index:', immutableIdx);
console.log('Nearby code (first 300 chars):');
console.log(nearbyCode.substring(0, 300));

if (!nearbyCode.includes('Freeze')) {
    console.log('FAIL: Missing Freeze in nearby code');
} else {
    console.log('PASS: Has Freeze in nearby code');
}

if (!nearbyCode.includes('identifier.id')) {
    console.log('FAIL: Missing identifier.id in nearby code');
} else {
    console.log('PASS: Has identifier.id in nearby code');
}
