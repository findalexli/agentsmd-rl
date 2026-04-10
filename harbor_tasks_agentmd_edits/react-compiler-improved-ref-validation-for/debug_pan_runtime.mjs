import fs from 'fs';

const src = fs.readFileSync(
    'compiler/packages/snap/src/sprout/shared-runtime.ts',
    'utf-8'
);

// Extract PanResponder export block
const match = src.match(/export const PanResponder = \{[\s\S]*?\n\};/);
if (!match) {
    console.error('PanResponder export not found in shared-runtime.ts');
    process.exit(1);
}

console.log('Matched code:');
console.log(match[0]);

// Strip TypeScript type annotations to get evaluable JS
let code = match[0]
    .replace('export const ', 'var ')
    .replace(/\(obj:\s*any\):\s*any/g, '(obj)');

console.log('\nTransformed code:');
console.log(code);

eval(code);

// Verify PanResponder.create returns its input (freeze semantics)
const input = { onPanResponderTerminate: () => {} };
const result = PanResponder.create(input);
if (result !== input) {
    console.error('PanResponder.create should return its input argument');
    process.exit(1);
}
if (typeof PanResponder.create !== 'function') {
    console.error('PanResponder.create must be a function');
    process.exit(1);
}
console.log('PASS');
