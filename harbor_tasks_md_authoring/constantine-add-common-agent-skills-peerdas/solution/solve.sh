#!/usr/bin/env bash
set -euo pipefail

cd /workspace/constantine

# Idempotency guard
if grep -qF "Use the `toHex()` functions for quick inspection of cryptographic values. **You " ".agents/skills/debugging/SKILL.md" && grep -qF "description: Profile and identify performance bottlenecks in Constantine cryptog" ".agents/skills/performance-investigation/SKILL.md" && grep -qF "When memory allocation is necessary, for example for multithreading, GPU computi" ".agents/skills/seq-arrays-openarrays-slicing-views/SKILL.md" && grep -qF "func serializeBatchUncompressed_vartime*(dst: ptr UncheckedArray[array[64, byte]" ".agents/skills/serialization-hex-debugging/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/debugging/SKILL.md b/.agents/skills/debugging/SKILL.md
@@ -0,0 +1,114 @@
+---
+name: constantine-debugging
+description: Constantine debugging techniques and tools
+license: MIT
+compatibility: opencode
+metadata:
+  audience: developers
+  language: nim
+---
+
+## What I do
+
+Cover debugging techniques for Constantine cryptographic code.
+
+## Quick Debugging
+
+### debugEcho
+
+Use `debugEcho` instead of `echo` to avoid side-effect warnings in `func` procedures:
+
+```nim
+# Bad - echo has side effects, triggers compiler warnings in funcs
+echo "Value: ", value
+
+# Good - debugEcho is allowed in debug code
+debugEcho "Value: ", value.toHex()
+```
+
+### toHex for Quick Output
+
+Use the `toHex()` functions for quick inspection of cryptographic values. **You must import the corresponding IO module**:
+
+```nim
+# Field elements (Fr, Fp)
+import constantine/math/io/io_fields
+debugEcho "Scalar: ", scalar.toHex()
+
+# Elliptic curve points
+import constantine/math/io/io_ec
+debugEcho "Point: ", point.toHex()
+
+# BigInts
+import constantine/math/io/io_bigints
+debugEcho "BigInt: ", bigInt.toHex()
+
+# Extension fields (Fp2, Fp4, Fp6, Fp12)
+import constantine/math/io/io_extfields
+debugEcho "Fp2: ", fp2.toHex()
+```
+
+## Conditional Debug Code
+
+### debug: Template
+
+Code guarded by `debug:` from `constantine/platforms/primitives.nim` is only compiled when `-d:CTT_DEBUG` is defined:
+
+```nim
+from constantine/platforms/primitives import debug
+
+debug:
+  # This code only compiles with -d:CTT_DEBUG
+  debugEcho "Debug info: ", value.toHex()
+  doAssert someCondition, "Debug assertion failed"
+```
+
+Compile with:
+```bash
+nim c -d:CTT_DEBUG your_file.nim
+```
+
+## Full Stack Traces
+
+In release mode, code is optimized and stack traces may be incomplete. Use `-d:linetrace` for full stack traces:
+
+```bash
+# Full stack traces in release mode
+nim c -d:release -d:linetrace your_file.nim
+```
+
+This is often necessary because:
+- Release mode with `-d:release` is needed for realistic performance
+- But `-d:release` removes debug info by default
+- `-d:linetrace` restores full stack traces while keeping optimizations
+
+## Complex Debug Blocks
+
+For complex debugging that can't use `debugEcho`, wrap in `{.cast(noSideEffect).}`:
+
+```nim
+{.cast(noSideEffect).}:
+  block:
+    # Complex debug code here
+    echo "Debug info: ", someVar
+    echo "More info: ", anotherVar.toHex()
+```
+
+## Required Imports for toHex
+
+| Type | Import |
+|------|--------|
+| Field elements (Fp, Fr) | `constantine/math/io/io_fields` |
+| Elliptic curve points | `constantine/math/io/io_ec` |
+| BigInts | `constantine/math/io/io_bigints` |
+| Extension fields (Fp2, Fp4...) | `constantine/math/io/io_extfields` |
+
+## Debugging Tips
+
+1. **Import the right IO module** - toHex won't work without it
+2. **Start with toHex** - Quickest way to see values
+3. **Use debugEcho** - For simple prints in func procedures
+4. **Use debug: template** - For code that should only exist in debug builds
+5. **Use {.cast(noSideEffect).}** - For complex debug blocks in funcs
+6. **Use -d:CTT_DEBUG** - For conditional compilation of debug code
+7. **Use -d:linetrace** - For full stack traces in release mode
diff --git a/.agents/skills/performance-investigation/SKILL.md b/.agents/skills/performance-investigation/SKILL.md
@@ -0,0 +1,126 @@
+---
+name: performance-investigation
+description: Profile and identify performance bottlenecks in Constantine cryptographic code using metering and benchmarking tools
+license: MIT
+compatibility: opencode
+metadata:
+  audience: developers
+  language: nim
+  domain: cryptography
+---
+
+## What I do
+
+Help identify and analyze performance bottlenecks in Constantine cryptographic implementations through:
+
+- **Metering**: Count operations (field mul, add, EC ops, scalar muls) with `-d:CTT_METER` flag
+- **Benchmarking**: Measure ops/s, ns/op, CPU cycles with `-d:danger` flag
+- **Profiling**: Create small test binaries for detailed analysis with perf or similar tools
+- **Comparison**: Compare implementations against reference (e.g., C-kzg-4844)
+
+## When to use me
+
+Use this skill when:
+
+1. **Implementation is slower than expected** (e.g., 50% slower than reference)
+2. **Need to identify hotspots** in cryptographic algorithms (FK20, FFT, MSM, pairings)
+3. **Optimizing critical paths** in PeerDAS (EIP-7594) or KZG (EIP-4844) code
+4. **Validating algorithmic complexity** (e.g., O(n log n) vs O(n²))
+5. **Comparing optimization strategies** (fixed-base vs variable-base MSM)
+
+## How to investigate performance
+
+### Step 1: Enable Metering
+
+Add `{.meter.}` pragma to suspect procedures:
+
+```nim
+import constantine/platforms/abstractions  # Re-exports metering/tracer
+
+proc hotspotFunction*(...) {.meter.} =
+  # This will be tracked when compiled with -d:CTT_METER
+```
+
+### Step 2: Create Test Binary
+
+Create a minimal test file in `metering/` or `build/`:
+
+```nim
+# metering/m_your_test.nim
+import
+  constantine/platforms/metering/[reports, tracer],
+  # ... your imports
+
+proc main() =
+  resetMetering()
+  yourFunction()
+  reportCli(Metrics, "UseAssembly")
+
+when isMainModule:
+  main()
+```
+
+### Step 3: Compile with Metering
+
+```bash
+nim c -r --hints:off --warnings:off --verbosity:0 \
+  -d:danger -d:CTT_METER \
+  --outdir:build \
+  metering/m_your_test.nim
+```
+
+### Step 4: Analyze Output
+
+Metering output shows:
+- **# of Calls**: How many times each proc was called
+- **Throughput (ops/s)**: Operations per second
+- **Time (µs)**: Total and average time per call
+- **CPU cycles**: Approximate cycle count (indicative only)
+
+Look for:
+- High call counts × high avg time = **primary bottleneck**
+- EC operations (scalarMul, multiScalarMul) are typically 100-1000× slower than field ops
+- Variable-base MSM vs fixed-base MSM can differ by 5-10×
+
+### Step 5: For Detailed Profiling
+
+Compile a small binary for perf:
+
+```bash
+nim c -d:danger --debugger:native \
+  --outdir:build \
+  metering/m_your_test.nim
+
+# Then use perf, vtune, or similar
+perf record -- ./build/m_your_test
+perf report
+```
+
+## Key Patterns in Constantine
+
+### Metering Infrastructure
+
+- **`constantine/platforms/metering/tracer.nim`**: Defines `{.meter.}` macro
+- **`constantine/platforms/metering/reports.nim`**: CLI reporting
+- **`constantine/platforms/abstractions.nim`**: Re-exports metering primitives
+- **Flag**: `-d:CTT_METER` enables metering (off by default)
+
+### Common Bottlenecks
+
+1. **Scalar Multiplication** (`scalarMul_vartime`)
+
+2. **Multi-Scalar Multiplication** (`multiScalarMul_vartime`)
+   - Look for Pippenger vs fixed-base optimization opportunities
+
+3. **FFT Operations** (`fft_nr`, `ec_fft_nr`)
+
+4. **Field Operations** (`prod`, `square`, `inv`)
+   - `inv` and `inv_vartime` are much slower than mul (~100×)
+   - Batch inversion can help
+
+## Notes
+
+- **Metering overhead**: Metering adds ~10-20% overhead; use for relative comparison, not absolute timing
+- **Cycle counts**: CPU cycle measurements are approximate (affected by turbo boost, throttling)
+- **Compiler effects**: GCC vs Clang can differ significantly on bigint arithmetic
+- **Assembly**: Constantine's compile-time assembler improves performance; check `UseASM_X86_64` flag
\ No newline at end of file
diff --git a/.agents/skills/seq-arrays-openarrays-slicing-views/SKILL.md b/.agents/skills/seq-arrays-openarrays-slicing-views/SKILL.md
@@ -0,0 +1,152 @@
+---
+name: seq-arrays-openarrays-slicing-views
+description: Nim seq, arrays, openarray, slicing, and views best practices for zero-allocation cryptographic code
+license: MIT
+compatibility: opencode
+metadata:
+  audience: developers
+  language: nim
+---
+
+## What I do
+
+Provide guidance on working with dynamically-sized buffers in Nim for cryptographic code.
+
+Emphasizes avoiding `seq` in favor of auditable memory management through Constantine's shim over the system allocator.
+
+Avoid Nim slicing syntax `..<` slice syntax on arrays, sequences and openarrays as it creates an intermediate seq, which:
+- Causes an avoidable heap allocation
+- Allocates using Nim allocator
+- Violates no-alloc conventions in cryptographic code that handle secrets
+- Can trigger side-channel vulnerabilities
+
+## Why No seq?
+
+We actively avoid memory allocation for any protocol that:
+- handle secrets
+- could be expected to run in a trusted enclave or embedded devices
+
+This includes encryption, hashing and signatures protocols.
+
+When memory allocation is necessary, for example for multithreading, GPU computing or succinct or zero-knowledge proof protocol, we use custom allocators from `constantine/platforms/allocs.nim`. Those are thin wrappers around the OS `malloc`/`free` with effect tracking `{.tags:[HeapAlloc].}` or `{.tags:[Alloca].}`. Then we can use Nim's effect tracking `{.tags:[].}` to ensure no *heap allocation* or *alloca* is used in the call stack of specific functions.
+
+```nim
+# Compiler tracked heap allocation
+let ptr = allocHeapArrayAligned(int, 128, alignment = 64)
+
+# Compiler tracked stack allocation
+let stackPtr = allocStackArray(int, 128)
+
+# Don't do this in cryptographic code!
+let bad = @[1, 2, 3]  # seq - hidden allocation!
+```
+
+## Array/View Types Overview
+
+### array[T, U]
+- Fixed size, stack-allocated
+- Safe for cryptographic constants
+- Use `sizeof` to compute total size for heap allocation
+
+### openArray[T]
+- A virtual type (ptr + length) passed by value
+- Cannot be stored in types or returned from functions
+- Slicing with `[a ..< b]` creates an intermediate **seq** (heap allocation!)
+- Use .toOpenArray(start, stopInclusive) instead
+
+### ptr UncheckedArray[T]
+- Raw pointer to contiguous memory
+- Can be stored in types
+- Use `cast[ptr UncheckedArray[T]](addr)` or `.asUnchecked()` to convert
+
+### View[T]
+- A Nim type storing (ptr + length)
+- Can be stored in types or returned from functions
+- Convert to openArray via `.toOpenArray` template
+
+### StridedView[T]
+- For non-contiguous data (e.g., FFT even/odd splitting)
+- Stores: data ptr, length, stride, offset
+
+## Converting Between Types
+
+### openArray to ptr UncheckedArray
+```nim
+# PREFERRED: Using views.nim (import constantine/platforms/views)
+let ptrArr = oa.asUnchecked()
+
+# Alternative: Using cast
+let ptrArr = cast[ptr UncheckedArray[T]](oa[0].unsafeAddr)
+```
+
+### ptr UncheckedArray to openArray
+```nim
+# Using system.nim (start, stopInclusive) - default
+let oa = toOpenArray(ptrArr, start, stopInclusive)
+
+# Using views.nim (ptr, length) - convenience template
+let oa = toOpenArray(ptrArr, length)
+# Or simply: ptrArr.toOpenArray(len)
+```
+
+### openArray to View
+```nim
+let v = toView(oa)
+# Or: View[T](data: cast[ptr UncheckedArray[T]](oa[0].unsafeAddr), len: oa.len)
+```
+
+## Slicing Without seq Creation
+
+NEVER use slice syntax like `array[0 ..< len]` on openArray parameters - this creates a seq (heap allocation).
+
+Instead use:
+```nim
+# Bad - creates seq!
+process(data[0 ..< count])
+
+# Good - no allocation (system.nim uses stopInclusive)
+process(data.toOpenArray(0, count-1))
+```
+
+`ptr UncheckedArray` should use the ptr+len syntax from `import constantine/platforms/views`
+
+```
+# Good - using views.nim convenience (ptr, length)
+process(myDataPtr.toOpenArray(count))
+```
+
+## Constantine Allocator
+
+ Constantine provides tracked memory management in `constantine/platforms/allocs.nim`:
+
+### Stack Allocation
+```nim
+template allocStack*(T: typedesc): ptr T
+template allocStackUnchecked*(T: typedesc, size: int): ptr T
+template allocStackArray*(T: typedesc, len: SomeInteger): ptr UncheckedArray[T]
+```
+
+### Heap Allocation
+```nim
+proc allocHeap*(T: typedesc): ptr T
+proc allocHeapUnchecked*(T: typedesc, size: int): ptr T
+proc allocHeapArray*(T: typedesc, len: SomeInteger): ptr UncheckedArray[T]
+proc allocHeapAligned*(T: typedesc, alignment: static Natural): ptr T
+proc allocHeapArrayAligned*(T: typedesc, len: int, alignment: static Natural): ptr UncheckedArray[T]
+proc alloc0HeapArrayAligned*(T: typedesc, len: int, alignment: static Natural): ptr UncheckedArray[T]
+  ## Allocation + zero initialization
+```
+
+## varargs
+
+Nim varargs can accept:
+- Arrays: `foo([1, 2, 3])`
+- Seqs: `foo(@[1, 2, 3])` - **avoid in crypto code**
+- OpenArray: `foo(someOpenArray)`
+- Direct args: `foo(1, 2, 3)`
+
+## When to use me
+
+- Working with Constantine library code
+- When slicing buffers
+- When needing dynamic memory management
diff --git a/.agents/skills/serialization-hex-debugging/SKILL.md b/.agents/skills/serialization-hex-debugging/SKILL.md
@@ -0,0 +1,271 @@
+---
+name: serialization-hex-debugging
+description: Constantine serialization and hex debugging conventions
+license: MIT
+compatibility: opencode
+metadata:
+  audience: developers
+  language: nim
+---
+
+## What I do
+
+Cover serialization patterns and debugging practices in Constantine library.
+
+## Serialization Conventions
+
+### Status Codes
+
+Serialization functions return status codes, never exceptions:
+
+```nim
+type
+  CttCodecScalarStatus* = enum
+    cttCodecScalar_Success
+    cttCodecScalar_Zero
+    cttCodecScalar_ScalarLargerThanCurveOrder
+
+  CttCodecEccStatus* = enum
+    cttCodecEcc_Success
+    cttCodecEcc_InvalidEncoding
+    cttCodecEcc_CoordinateGreaterThanOrEqualModulus
+    cttCodecEcc_PointNotOnCurve
+    cttCodecEcc_PointNotInSubgroup
+    cttCodecEcc_PointAtInfinity
+```
+
+### Parsing Functions (bytes → internal)
+
+- `unmarshal(dst: var BigInt, src: openArray[byte], endianness)` - returns bool
+- `deserialize_*` - for cryptographic types, returns status code
+- `fromBytes`, `fromHex` - alternative names
+- `fromUint*(dst: var FF, src: SomeUnsignedInt)` - parse small unsigned integers into field elements
+
+### Serialization Functions (internal → bytes)
+
+- `marshal(dst: var openArray[byte], src, endianness)` - returns bool
+- `serialize_*` - for cryptographic types
+- `toBytes`, `toHex` - alternative names
+
+### BLS12-381 Serialization Functions
+
+From `constantine/serialization/codecs_bls12_381.nim`:
+
+```nim
+# Scalar (Fr) - 32 bytes
+func serialize_scalar*(dst: var array[32, byte], scalar: Fr[BLS12_381].getBigInt()): CttCodecScalarStatus
+func deserialize_scalar*(dst: var Fr[BLS12_381].getBigInt(), src: array[32, byte]): CttCodecScalarStatus
+
+# G1 Point (compressed) - 48 bytes
+func serialize_g1_compressed*(dst: var array[48, byte], g1P: EC_ShortW_Aff[Fp[BLS12_381], G1]): CttCodecEccStatus
+func deserialize_g1_compressed*(dst: var EC_ShortW_Aff[Fp[BLS12_381], G1], src: array[48, byte]): CttCodecEccStatus
+func deserialize_g1_compressed_unchecked*(dst: var EC_ShortW_Aff[Fp[BLS12_381], G1], src: array[48, byte]): CttCodecEccStatus
+
+# G2 Point (compressed) - 96 bytes
+func serialize_g2_compressed*(dst: var array[96, byte], g2P: EC_ShortW_Aff[Fp2[BLS12_381], G2]): CttCodecEccStatus
+func deserialize_g2_compressed*(dst: var EC_ShortW_Aff[Fp2[BLS12_381], G2], src: array[96, byte]): CttCodecEccStatus
+func deserialize_g2_compressed_unchecked*(dst: var EC_ShortW_Aff[Fp2[BLS12_381], G2], src: array[96, byte]): CttCodecEccStatus
+
+# Validation (expensive, can be cached)
+func validate_scalar*(scalar: Fr[BLS12_381].getBigInt()): CttCodecScalarStatus
+func validate_g1*(g1P: EC_ShortW_Aff[Fp[BLS12_381], G1]): CttCodecEccStatus
+func validate_g2*(g2P: EC_ShortW_Aff[Fp2[BLS12_381], G2]): CttCodecEccStatus
+```
+
+### Banderwagon Serialization Functions
+
+From `constantine/serialization/codecs_banderwagon.nim`:
+
+```nim
+# Scalar - 32 bytes (big-endian)
+func serialize_scalar*(dst: var array[32, byte], scalar: Fr[Banderwagon].getBigInt(), order: static Endianness = bigEndian): CttCodecScalarStatus
+func serialize_fr*(dst: var array[32, byte], scalar: Fr[Banderwagon], order: static Endianness = bigEndian): CttCodecScalarStatus
+func deserialize_scalar*(dst: var Fr[Banderwagon].getBigInt(), src: array[32, byte], order: static Endianness = bigEndian): CttCodecScalarStatus
+func deserialize_fr*(dst: var Fr[Banderwagon], src: array[32, byte], order: static Endianness = bigEndian): CttCodecScalarStatus
+
+# Point (compressed) - 32 bytes
+func serialize*(dst: var array[32, byte], P: EC_TwEdw_Aff[Fp[Banderwagon]]): CttCodecEccStatus
+func serializeUncompressed*(dst: var array[64, byte], P: EC_TwEdw_Aff[Fp[Banderwagon]]): CttCodecEccStatus
+func deserialize_unchecked_vartime*(dst: var EC_TwEdw_Aff[Fp[Banderwagon]], src: array[32, byte]): CttCodecEccStatus
+func deserialize_vartime*(dst: var EC_TwEdw_Aff[Fp[Banderwagon]], src: array[32, byte]): CttCodecEccStatus
+func deserializeUncompressed*(dst: var EC_TwEdw_Aff[Fp[Banderwagon]], src: array[64, byte]): CttCodecEccStatus
+func deserializeUncompressed_unchecked*(dst: var EC_TwEdw_Aff[Fp[Banderwagon]], src: array[64, byte]): CttCodecEccStatus
+
+# Batch serialization
+func serializeBatch_vartime*(dst: ptr UncheckedArray[array[32, byte]], points: ptr UncheckedArray[EC_TwEdw_Prj[Fp[Banderwagon]]], N: int): CttCodecEccStatus
+func serializeBatchUncompressed_vartime*(dst: ptr UncheckedArray[array[64, byte]], points: ptr UncheckedArray[EC_TwEdw_Prj[Fp[Banderwagon]]], N: int): CttCodecEccStatus
+```
+
+### ECDSA Serialization Functions
+
+From `constantine/serialization/codecs_ecdsa.nim`:
+
+```nim
+# ASN.1 DER signature (generic over curve)
+type DerSignature*[N: static int] = object
+  data*: array[N, byte]
+  len*: int
+
+proc toDER*[Name: static Algebra; N: static int](derSig: var DerSignature[N], r, s: Fr[Name])
+proc fromDER*(r, s: var array[32, byte], derSig: DerSignature)
+proc fromRawDER*(r, s: var array[32, byte], sig: openArray[byte]): bool
+```
+
+### Generic Codecs
+
+From `constantine/serialization/codecs.nim`:
+
+```nim
+# Hex conversion
+func toHex*(bytes: openarray[byte]): string
+func fromHex*(dst: var openArray[byte], hex: openArray[char])
+func paddedFromHex*(output: var openArray[byte], hexStr: openArray[char], order: static[Endianness])
+
+# Base64
+func base64_decode*(dst: var openArray[byte], src: openArray[char]): int
+```
+
+### Limbs I/O
+
+From `constantine/serialization/io_limbs.nim`:
+
+```nim
+# Low-level limbs serialization
+func unmarshal*(dst: var openArray[T], src: openarray[byte], wordBitWidth: static int, srcEndianness: static Endianness): bool
+func marshal*(dst: var openArray[byte], src: openArray[T], wordBitWidth: static int, dstEndianness: static Endianness): bool
+```
+
+### Working with Small Integers
+
+When you need to set a field element or BigInt to a small constant value (0, 1, 2, etc.), use `fromUint` or `setUint`:
+
+```nim
+# For field elements (Fp, Fr)
+from constantine/math/io/io_fields import fromUint
+var x: Fr[BLS12_381]
+x.fromUint(1)           # Set to 1
+x.fromUint(42)          # Set to 42
+
+# For BigInts
+from constantine/math/arithmetic/bigints import setUint
+var big: BigInt[256]
+big.setUint(1)          # Set to 1 (in-place)
+big.setUint(42)         # Set to 42
+
+# Also available as fromUint for BigInt
+let big2 = BigInt[256].fromUint(123)
+```
+
+### Endianness
+
+- Ethereum spec v1.6.1+ uses **big-endian** (`KZG_ENDIANNESS = 'big'`) for field/scalar elements
+  - Note: This changed from little-endian in spec v1.3.0
+  - Reference: https://github.com/ethereum/consensus-specs/blob/v1.6.1/specs/deneb/polynomial-commitments.md#constants
+- BLS12-381 uses **big-endian** for serialization (Zcash format)
+- Banderwagon uses **big-endian**
+- Big-endian is common for byte serialization in other contexts
+- Always specify explicitly: `marshal(dst, src, bigEndian)`
+
+### Byte Manipulation Utilities
+
+From `constantine/serialization/endians.nim`:
+
+```nim
+# Low-level byte conversion (compile-time safe)
+template toByte*(x: SomeUnsignedInt): byte
+
+# Convert unsigned int to bytes
+func toBytes*(num: SomeUnsignedInt, endianness: static Endianness): array[sizeof(num), byte]
+
+# Read unsigned int from bytes (multiple overloads)
+func fromBytes*(T: type SomeUnsignedInt, bytes: array[sizeof(T), byte], endianness: static Endianness): T
+func fromBytes*(T: type SomeUnsignedInt, bytes: openArray[byte], offset: int, endianness: static Endianness): T
+func fromBytes*(T: type SomeUnsignedInt, bytes: ptr UncheckedArray[byte], offset: int, endianness: static Endianness): T
+
+# Write integer into raw binary blob
+# - blobFrom: The whole array is interpreted as little-endian or big-endian (blobEndianness)
+# - dumpRawInt: The array is little-endian by convention, but words inside are endian-aware (wordEndianness)
+func blobFrom*(dst: var openArray[byte], src: SomeUnsignedInt, startIdx: int, endian: static Endianness)
+func dumpRawInt*(dst: var openArray[byte], src: SomeUnsignedInt, cursor: int, endian: static Endianness)
+```
+
+**Key difference:**
+- `blobFrom(blobEndianness)`: The entire byte array is interpreted as either little-endian or big-endian.
+- `dumpRawInt(wordEndianness)`: The array is little-endian by convention, but the individual words are written with the specified endianness.
+
+### Example Pattern
+
+```nim
+func bytes_to_bls_field*(dst: var Fr[BLS12_381], src: array[32, byte]): CttCodecScalarStatus =
+  var scalar {.noInit.}: Fr[BLS12_381].getBigInt()
+  let status = scalar.deserialize_scalar(src)
+  if status notin {cttCodecScalar_Success, cttCodecScalar_Zero}:
+    return status
+  dst.fromBig(scalar)
+  return cttCodecScalar_Success
+```
+
+## Debugging
+
+### IO Modules
+
+For debugging, use the IO modules:
+
+- `constantine/math/io/io_fields.nim` - Fp/Fr serialization
+- `constantine/math/io/io_ec.nim` - Elliptic curve points
+- `constantine/math/io/io_bigints.nim` - BigInt serialization
+- `constantine/math/io/io_extfields.nim` - Extension fields (Fp2, Fp4, etc.)
+
+### Key Functions
+
+```nim
+# Hex output (for debugging only, not constant-time)
+func toHex*(f: FF): string
+func toHex*(P: EC_ShortW_Aff): string
+
+# Marshal to byte array
+func marshal*(dst: var openArray[byte], src: FF, endianness): bool
+
+# From hex string
+func fromHex*(dst: var FF, hexString: string)
+```
+
+### Required Imports for debug toHex Functions
+
+| Type | Import |
+|------|--------|
+| Field elements (Fp, Fr) | `constantine/math/io/io_fields` |
+| Elliptic curve points | `constantine/math/io/io_ec` |
+| BigInts | `constantine/math/io/io_bigints` |
+| Extension fields (Fp2, Fp4...) | `constantine/math/io/io_extfields` |
+
+### Debug Echo
+
+Use `debugEcho` instead of `echo` to avoid side-effect warnings in `func` procedures:
+
+```nim
+# Bad - echo has side effects
+echo "Value: ", value
+
+# Good - debugEcho is allowed in debug code
+debugEcho "Value: ", value.toHex()
+```
+
+### Complex Debug Blocks
+
+For complex debugging that can't use `debugEcho`, wrap in `{.cast(noSideEffect).}`:
+
+```nim
+{.cast(noSideEffect).}:
+  block:
+    # Complex debug code here
+    # Can use echo, print, etc.
+    echo "Debug info: ", someVar
+```
+
+## No seq/strings in crypto code
+
+Serialization in hot paths must avoid heap allocation:
+- Never use `seq[byte]` or `string`
+- Use fixed-size arrays or `openArray`
+- Use `transcript.update(data)` instead of building a seq
PATCH

echo "Gold patch applied."
