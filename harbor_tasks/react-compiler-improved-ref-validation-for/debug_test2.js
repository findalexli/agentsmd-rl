import fs from 'fs';

const src = fs.readFileSync(
    'compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts',
    'utf-8'
);

const immutableIdx = src.indexOf("case 'ImmutableCapture':");
console.log('ImmutableCapture at:', immutableIdx);

for (let size of [400, 500, 600, 700, 800, 1000]) {
    const nearbyCode = src.slice(immutableIdx, immutableIdx + size);
    const hasFreeze = nearbyCode.includes('e.kind === \'Freeze\'');
    const hasId = nearbyCode.includes('identifier.id');
    console.log(`Size ${size}: hasFreeze=${hasFreeze}, hasId=${hasId}`);
}

// Check the actual code that needs to be detected
const largerSlice = src.slice(immutableIdx, immutableIdx + 1000);
console.log('\nActual Freeze check code:');
const freezeMatch = largerSlice.match(/e\.kind ===? ['"]Freeze['"]/);
console.log(freezeMatch ? freezeMatch[0] : 'not found');
