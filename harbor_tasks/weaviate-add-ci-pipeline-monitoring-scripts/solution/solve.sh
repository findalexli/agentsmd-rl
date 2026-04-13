#!/bin/bash
# Gold patch: fix the calculateAverage function to return 0 instead of null for empty arrays

cat > /workspace/sample_repo/index.js << 'EOF'
// Sample function with bug fixed
// Fix: return 0 instead of null for empty arrays

function calculateAverage(numbers) {
  if (!numbers || numbers.length === 0) {
    return 0;  // Fixed: was returning null
  }

  const sum = numbers.reduce((acc, n) => acc + n, 0);
  return sum / numbers.length;
}

function calculateSum(numbers) {
  if (!numbers) {
    return 0;
  }
  return numbers.reduce((acc, n) => acc + n, 0);
}

module.exports = { calculateAverage, calculateSum };
EOF
