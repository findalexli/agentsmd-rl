# Agent Config Files for pytorch-wheel-tag-freethreaded-abi

Repo: pytorch/pytorch
Commit: 8eaba043803b82549bf4fb42d5e03099be2eb1d9
Files found: 40


---
## .ci/pytorch/README.md

```
   1 | This directory contains scripts for our continuous integration.
```


---
## .claude/skills/add-uint-support/SKILL.md

```
   1 | ---
   2 | name: add-uint-support
   3 | description: Add unsigned integer (uint) type support to PyTorch operators by updating AT_DISPATCH macros. Use when adding support for uint16, uint32, uint64 types to operators, kernels, or when user mentions enabling unsigned types, barebones unsigned types, or uint support.
   4 | ---
   5 | 
   6 | # Add Unsigned Integer (uint) Support to Operators
   7 | 
   8 | This skill helps add support for unsigned integer types (uint16, uint32, uint64) to PyTorch operators by updating their AT_DISPATCH macros.
   9 | 
  10 | ## When to use this skill
  11 | 
  12 | Use this skill when:
  13 | - Adding uint16, uint32, or uint64 support to an operator
  14 | - User mentions "unsigned types", "uint support", "barebones unsigned types"
  15 | - Enabling support for kUInt16, kUInt32, kUInt64 in kernels
  16 | - Working with operator implementations that need expanded type coverage
  17 | 
  18 | ## Quick reference
  19 | 
  20 | **Add unsigned types to existing dispatch:**
  21 | ```cpp
  22 | // Before
  23 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  24 |   kernel<scalar_t>();
  25 | }), AT_EXPAND(AT_ALL_TYPES));
  26 | 
  27 | // After (method 1: add unsigned types explicitly)
  28 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  29 |   kernel<scalar_t>();
  30 | }), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES));
  31 | 
  32 | // After (method 2: use V2 integral types if AT_INTEGRAL_TYPES present)
  33 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  34 |   kernel<scalar_t>();
  35 | }), AT_EXPAND(AT_INTEGRAL_TYPES_V2), AT_EXPAND(AT_FLOATING_TYPES));
  36 | ```
  37 | 
  38 | ## Type group reference
  39 | 
  40 | **Unsigned type groups:**
  41 | - `AT_BAREBONES_UNSIGNED_TYPES`: kUInt16, kUInt32, kUInt64
  42 | - `AT_INTEGRAL_TYPES_V2`: AT_INTEGRAL_TYPES + AT_BAREBONES_UNSIGNED_TYPES
  43 | 
  44 | **Relationship:**
  45 | ```cpp
  46 | AT_INTEGRAL_TYPES          // kByte, kChar, kInt, kLong, kShort
  47 | AT_BAREBONES_UNSIGNED_TYPES  // kUInt16, kUInt32, kUInt64
  48 | AT_INTEGRAL_TYPES_V2       // INTEGRAL_TYPES + BAREBONES_UNSIGNED_TYPES
  49 | ```
  50 | 
  51 | ## Instructions
  52 | 
  53 | ### Step 1: Determine if conversion to V2 is needed
  54 | 
  55 | Check if the file uses AT_DISPATCH_V2:
  56 | 
  57 | **If using old AT_DISPATCH:**
  58 | - First convert to AT_DISPATCH_V2 using the at-dispatch-v2 skill
  59 | - Then proceed with adding uint support
  60 | 
  61 | **If already using AT_DISPATCH_V2:**
  62 | - Proceed directly to Step 2
  63 | 
  64 | ### Step 2: Analyze the current dispatch macro
  65 | 
  66 | Identify what type groups are currently in use:
  67 | 
  68 | ```cpp
  69 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  70 |   // body
  71 | }), AT_EXPAND(AT_ALL_TYPES), kHalf, kBFloat16);
  72 |     ^^^^^^^^^^^^^^^^^^^^^^^^^
  73 |     Current type coverage
  74 | ```
  75 | 
  76 | Common patterns:
  77 | - `AT_EXPAND(AT_ALL_TYPES)` → includes AT_INTEGRAL_TYPES + AT_FLOATING_TYPES
  78 | - `AT_EXPAND(AT_INTEGRAL_TYPES)` → signed integers only
  79 | - `AT_EXPAND(AT_FLOATING_TYPES)` → floating point types
  80 | 
  81 | ### Step 3: Choose the uint addition method
  82 | 
  83 | Two approaches:
  84 | 
  85 | **Method 1: Add AT_BAREBONES_UNSIGNED_TYPES explicitly**
  86 | - Use when: You want to be explicit about adding uint support
  87 | - Add `AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES)` to the type list
  88 | 
  89 | **Method 2: Substitute AT_INTEGRAL_TYPES with AT_INTEGRAL_TYPES_V2**
  90 | - Use when: The dispatch already uses `AT_EXPAND(AT_INTEGRAL_TYPES)`
  91 | - More concise: replaces one type group with its superset
  92 | - Only applicable if AT_INTEGRAL_TYPES is present
  93 | 
  94 | ### Step 4: Apply the transformation
  95 | 
  96 | **Method 1 example:**
  97 | ```cpp
  98 | // Before
  99 | AT_DISPATCH_V2(
 100 |     dtype,
 101 |     "min_values_cuda",
 102 |     AT_WRAP([&]() {
 103 |       kernel_impl<scalar_t>(iter);
 104 |     }),
 105 |     AT_EXPAND(AT_ALL_TYPES),
 106 |     kBFloat16, kHalf, kBool
 107 | );
 108 | 
 109 | // After (add unsigned types)
 110 | AT_DISPATCH_V2(
 111 |     dtype,
 112 |     "min_values_cuda",
 113 |     AT_WRAP([&]() {
 114 |       kernel_impl<scalar_t>(iter);
 115 |     }),
 116 |     AT_EXPAND(AT_ALL_TYPES),
 117 |     AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES),
 118 |     kBFloat16, kHalf, kBool
 119 | );
 120 | ```
 121 | 
 122 | **Method 2 example:**
 123 | ```cpp
 124 | // Before
 125 | AT_DISPATCH_V2(
 126 |     dtype,
 127 |     "integral_op",
 128 |     AT_WRAP([&]() {
 129 |       kernel<scalar_t>();
 130 |     }),
 131 |     AT_EXPAND(AT_INTEGRAL_TYPES)
 132 | );
 133 | 
 134 | // After (substitute with V2)
 135 | AT_DISPATCH_V2(
 136 |     dtype,
 137 |     "integral_op",
 138 |     AT_WRAP([&]() {
 139 |       kernel<scalar_t>();
 140 |     }),
 141 |     AT_EXPAND(AT_INTEGRAL_TYPES_V2)
 142 | );
 143 | ```
 144 | 
 145 | ### Step 5: Handle AT_ALL_TYPES vs individual type groups
 146 | 
 147 | If the dispatch uses `AT_EXPAND(AT_ALL_TYPES)`:
 148 | - `AT_ALL_TYPES` = `AT_INTEGRAL_TYPES` + `AT_FLOATING_TYPES`
 149 | - To add uint: add `AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES)` to the list
 150 | 
 151 | If the dispatch separately lists INTEGRAL and FLOATING:
 152 | ```cpp
 153 | // Before
 154 | AT_EXPAND(AT_INTEGRAL_TYPES), AT_EXPAND(AT_FLOATING_TYPES)
 155 | 
 156 | // After (Method 2 preferred)
 157 | AT_EXPAND(AT_INTEGRAL_TYPES_V2), AT_EXPAND(AT_FLOATING_TYPES)
 158 | ```
 159 | 
 160 | ### Step 6: Verify all dispatch sites
 161 | 
 162 | Check the file for ALL dispatch macros that need uint support:
 163 | - Some operators have multiple dispatch sites (CPU, CUDA, different functions)
 164 | - Apply the transformation consistently across all sites
 165 | - Ensure each gets the same type coverage updates
 166 | 
 167 | ### Step 7: Validate the changes
 168 | 
 169 | Check that:
 170 | - [ ] AT_DISPATCH_V2 format is used (not old AT_DISPATCH)
 171 | - [ ] Unsigned types are added via one of the two methods
 172 | - [ ] All relevant dispatch sites in the file are updated
 173 | - [ ] Type groups use `AT_EXPAND()`
 174 | - [ ] Arguments are properly formatted and comma-separated
 175 | 
 176 | ## Common patterns
 177 | 
 178 | ### Pattern 1: AT_ALL_TYPES + extras
 179 | 
 180 | ```cpp
 181 | // Before
 182 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
 183 |   kernel<scalar_t>();
 184 | }), AT_EXPAND(AT_ALL_TYPES), kHalf, kBFloat16);
 185 | 
 186 | // After
 187 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
 188 |   kernel<scalar_t>();
 189 | }), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES), kHalf, kBFloat16);
 190 | ```
 191 | 
 192 | ### Pattern 2: Separate INTEGRAL + FLOATING
 193 | 
 194 | ```cpp
 195 | // Before
 196 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
 197 |   kernel<scalar_t>();
 198 | }), AT_EXPAND(AT_INTEGRAL_TYPES), AT_EXPAND(AT_FLOATING_TYPES));
 199 | 
 200 | // After
 201 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
 202 |   kernel<scalar_t>();
 203 | }), AT_EXPAND(AT_INTEGRAL_TYPES_V2), AT_EXPAND(AT_FLOATING_TYPES));
 204 | ```
 205 | 
 206 | ### Pattern 3: Old dispatch needs conversion first
 207 | 
 208 | ```cpp
 209 | // Before (needs v2 conversion first)
 210 | AT_DISPATCH_ALL_TYPES_AND2(kHalf, kBFloat16, dtype, "op", [&]() {
 211 |   kernel<scalar_t>();
 212 | });
 213 | 
 214 | // After v2 conversion
 215 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
 216 |   kernel<scalar_t>();
 217 | }), AT_EXPAND(AT_ALL_TYPES), kHalf, kBFloat16);
 218 | 
 219 | // After adding uint support
 220 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
 221 |   kernel<scalar_t>();
 222 | }), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES), kHalf, kBFloat16);
 223 | ```
 224 | 
 225 | ## Multiple dispatch sites example
 226 | 
 227 | For a file with multiple functions:
 228 | 
 229 | ```cpp
 230 | void min_values_kernel_cuda(TensorIterator& iter) {
 231 |   AT_DISPATCH_V2(iter.dtype(), "min_values_cuda", AT_WRAP([&]() {
 232 |     impl<scalar_t>(iter);
 233 |   }), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES), kBFloat16, kHalf);
 234 |   //                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 235 |   //                           Added uint support
 236 | }
 237 | 
 238 | void min_launch_kernel(TensorIterator &iter) {
 239 |   AT_DISPATCH_V2(iter.input_dtype(), "min_cuda", AT_WRAP([&]() {
 240 |     gpu_reduce_kernel<scalar_t>(iter);
 241 |   }), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES), kBFloat16, kHalf);
 242 |   //                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 243 |   //                           Added uint support here too
 244 | }
 245 | ```
 246 | 
 247 | ## Decision tree
 248 | 
 249 | Use this decision tree to determine the approach:
 250 | 
 251 | ```
 252 | Is the file using AT_DISPATCH_V2?
 253 | ├─ No → Use at-dispatch-v2 skill first, then continue
 254 | └─ Yes
 255 |    └─ Does it use AT_EXPAND(AT_INTEGRAL_TYPES)?
 256 |       ├─ Yes → Replace with AT_EXPAND(AT_INTEGRAL_TYPES_V2)
 257 |       └─ No → Add AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES) to type list
 258 | ```
 259 | 
 260 | ## Edge cases
 261 | 
 262 | ### Case 1: Dispatch with only floating types
 263 | 
 264 | If the operator only supports floating point types, don't add uint support:
 265 | 
 266 | ```cpp
 267 | // Leave as-is - floating point only operator
 268 | AT_DISPATCH_V2(dtype, "float_op", AT_WRAP([&]() {
 269 |   kernel<scalar_t>();
 270 | }), AT_EXPAND(AT_FLOATING_TYPES), kHalf);
 271 | ```
 272 | 
 273 | ### Case 2: Complex types present
 274 | 
 275 | Unsigned types work alongside complex types:
 276 | 
 277 | ```cpp
 278 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
 279 |   kernel<scalar_t>();
 280 | }), AT_EXPAND(AT_ALL_TYPES),
 281 |     AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES),
 282 |     AT_EXPAND(AT_COMPLEX_TYPES),
 283 |     kHalf, kBFloat16);
 284 | ```
 285 | 
 286 | ### Case 3: Already has uint support
 287 | 
 288 | Check if uint types are already present:
 289 | - If `AT_INTEGRAL_TYPES_V2` is used → already has uint support
 290 | - If `AT_BAREBONES_UNSIGNED_TYPES` is already in list → already has uint support
 291 | - Skip the file if uint support is already present
 292 | 
 293 | ## Workflow
 294 | 
 295 | When asked to add uint support:
 296 | 
 297 | 1. Read the target file
 298 | 2. Check if using AT_DISPATCH_V2:
 299 |    - If not → use at-dispatch-v2 skill first
 300 | 3. Identify all dispatch macro sites
 301 | 4. For each dispatch:
 302 |    - Analyze current type groups
 303 |    - Choose method (add BAREBONES_UNSIGNED or upgrade to V2)
 304 |    - Apply transformation with Edit tool
 305 | 5. Show the user the changes
 306 | 6. Explain what was modified
 307 | 
 308 | ## Important notes
 309 | 
 310 | - Always check if v2 conversion is needed first
 311 | - Apply changes consistently across all dispatch sites in the file
 312 | - Method 2 (AT_INTEGRAL_TYPES_V2) is cleaner when applicable
 313 | - Method 1 (explicit AT_BAREBONES_UNSIGNED_TYPES) is more explicit
 314 | - Unsigned types are: kUInt16, kUInt32, kUInt64 (not kByte which is uint8)
 315 | - Some operators may not semantically support unsigned types - use judgment
 316 | 
 317 | ## Testing
 318 | 
 319 | After adding uint support, the operator should accept uint16, uint32, and uint64 tensors. The user is responsible for functional testing.
```


---
## .claude/skills/aoti-debug/SKILL.md

```
   1 | ---
   2 | name: aoti-debug
   3 | description: Debug AOTInductor (AOTI) errors and crashes. Use when encountering AOTI segfaults, device mismatch errors, constant loading failures, or runtime errors from aot_compile, aot_load, aoti_compile_and_package, or aoti_load_package.
   4 | ---
   5 | 
   6 | # AOTI Debugging Guide
   7 | 
   8 | This skill helps diagnose and fix common AOTInductor issues.
   9 | 
  10 | ## Error Pattern Routing
  11 | 
  12 | **Check the error message and route to the appropriate sub-guide:**
  13 | 
  14 | ### Triton Index Out of Bounds
  15 | If the error matches this pattern:
  16 | ```
  17 | Assertion `index out of bounds: 0 <= tmpN < ksM` failed
  18 | ```
  19 | **→ Follow the guide in `triton-index-out-of-bounds.md`**
  20 | 
  21 | ### All Other Errors
  22 | Continue with the sections below.
  23 | 
  24 | ---
  25 | 
  26 | ## First Step: Always Check Device and Shape Matching
  27 | 
  28 | **For ANY AOTI error (segfault, exception, crash, wrong output), ALWAYS check these first:**
  29 | 
  30 | 1. **Compile device == Load device**: The model must be loaded on the same device type it was compiled on
  31 | 2. **Input devices match**: Runtime inputs must be on the same device as the compiled model
  32 | 3. **Input shapes match**: Runtime input shapes must match the shapes used during compilation (or satisfy dynamic shape constraints)
  33 | 
  34 | ```python
  35 | # During compilation - note the device and shapes
  36 | model = MyModel().eval()           # What device? CPU or .cuda()?
  37 | inp = torch.randn(2, 10)           # What device? What shape?
  38 | compiled_so = torch._inductor.aot_compile(model, (inp,))
  39 | 
  40 | # During loading - device type MUST match compilation
  41 | loaded = torch._export.aot_load(compiled_so, "???")  # Must match model/input device above
  42 | 
  43 | # During inference - device and shapes MUST match
  44 | out = loaded(inp.to("???"))  # Must match compile device, shape must match
  45 | ```
  46 | 
  47 | **If any of these don't match, you will get errors ranging from segfaults to exceptions to wrong outputs.**
  48 | 
  49 | ## Key Constraint: Device Type Matching
  50 | 
  51 | **AOTI requires compile and load to use the same device type.**
  52 | 
  53 | - If you compile on CUDA, you must load on CUDA (device index can differ)
  54 | - If you compile on CPU, you must load on CPU
  55 | - Cross-device loading (e.g., compile on GPU, load on CPU) is NOT supported
  56 | 
  57 | ## Common Error Patterns
  58 | 
  59 | ### 1. Device Mismatch Segfault
  60 | 
  61 | **Symptom**: Segfault, exception, or crash during `aot_load()` or model execution.
  62 | 
  63 | **Example error messages**:
  64 | - `The specified pointer resides on host memory and is not registered with any CUDA device`
  65 | - Crash during constant loading in AOTInductorModelBase
  66 | - `Expected out tensor to have device cuda:0, but got cpu instead`
  67 | 
  68 | **Cause**: Compile and load device types don't match (see "First Step" above).
  69 | 
  70 | **Solution**: Ensure compile and load use the same device type. If compiled on CPU, load on CPU. If compiled on CUDA, load on CUDA.
  71 | 
  72 | ### 2. Input Device Mismatch at Runtime
  73 | 
  74 | **Symptom**: RuntimeError during model execution.
  75 | 
  76 | **Cause**: Input device doesn't match compile device (see "First Step" above).
  77 | 
  78 | **Better Debugging**: Run with `AOTI_RUNTIME_CHECK_INPUTS=1` for clearer errors. This flag validates all input properties including device type, dtype, sizes, and strides:
  79 | ```bash
  80 | AOTI_RUNTIME_CHECK_INPUTS=1 python your_script.py
  81 | ```
  82 | 
  83 | This produces actionable error messages like:
  84 | ```
  85 | Error: input_handles[0]: unmatched device type, expected: 0(cpu), but got: 1(cuda)
  86 | ```
  87 | 
  88 | 
  89 | ## Debugging CUDA Illegal Memory Access (IMA) Errors
  90 | 
  91 | If you encounter CUDA illegal memory access errors, follow this systematic approach:
  92 | 
  93 | ### Step 1: Sanity Checks
  94 | 
  95 | Before diving deep, try these debugging flags:
  96 | 
  97 | ```bash
  98 | AOTI_RUNTIME_CHECK_INPUTS=1
  99 | TORCHINDUCTOR_NAN_ASSERTS=1
 100 | ```
 101 | 
 102 | These flags take effect at compilation time (at codegen time):
 103 | 
 104 | - `AOTI_RUNTIME_CHECK_INPUTS=1` checks if inputs satisfy the same guards used during compilation
 105 | - `TORCHINDUCTOR_NAN_ASSERTS=1` adds codegen before and after each kernel to check for NaN
 106 | 
 107 | ### Step 2: Pinpoint the CUDA IMA
 108 | 
 109 | CUDA IMA errors can be non-deterministic. Use these flags to trigger the error deterministically:
 110 | 
 111 | ```bash
 112 | PYTORCH_NO_CUDA_MEMORY_CACHING=1
 113 | CUDA_LAUNCH_BLOCKING=1
 114 | ```
 115 | 
 116 | These flags take effect at runtime:
 117 | 
 118 | - `PYTORCH_NO_CUDA_MEMORY_CACHING=1` disables PyTorch's Caching Allocator, which allocates bigger buffers than needed immediately. This is usually why CUDA IMA errors are non-deterministic.
 119 | - `CUDA_LAUNCH_BLOCKING=1` forces kernels to launch one at a time. Without this, you get "CUDA kernel errors might be asynchronously reported" warnings since kernels launch asynchronously.
 120 | 
 121 | ### Step 3: Identify Problematic Kernels with Intermediate Value Debugger
 122 | 
 123 | Use the AOTI Intermediate Value Debugger to pinpoint the problematic kernel:
 124 | 
 125 | ```bash
 126 | AOT_INDUCTOR_DEBUG_INTERMEDIATE_VALUE_PRINTER=3
 127 | ```
 128 | 
 129 | This prints kernels one by one at runtime. Together with previous flags, this shows which kernel was launched right before the error.
 130 | 
 131 | To inspect inputs to a specific kernel:
 132 | 
 133 | ```bash
 134 | AOT_INDUCTOR_FILTERED_KERNELS_TO_PRINT="triton_poi_fused_add_ge_logical_and_logical_or_lt_231,_add_position_embeddings_kernel_5" AOT_INDUCTOR_DEBUG_INTERMEDIATE_VALUE_PRINTER=2
 135 | ```
 136 | 
 137 | If inputs to the kernel are unexpected, inspect the kernel that produces the bad input.
 138 | 
 139 | ## Additional Debugging Tools
 140 | 
 141 | ### Logging and Tracing
 142 | 
 143 | - **tlparse / TORCH_TRACE**: Provides complete output codes and records guards used
 144 | - **TORCH_LOGS**: Use `TORCH_LOGS="+inductor,output_code"` to see more PT2 internal logs
 145 | - **TORCH_SHOW_CPP_STACKTRACES**: Set to `1` to see more stack traces
 146 | 
 147 | ### Common Sources of Issues
 148 | 
 149 | - **Dynamic shapes**: Historically a source of many IMAs. Pay special attention when debugging dynamic shape scenarios.
 150 | - **Custom ops**: Especially when implemented in C++ with dynamic shapes. The meta function may need to be Symint'ified.
 151 | 
 152 | ## API Notes
 153 | 
 154 | ### Deprecated API
 155 | ```python
 156 | torch._export.aot_compile()  # Deprecated
 157 | torch._export.aot_load()     # Deprecated
 158 | ```
 159 | 
 160 | ### Current API
 161 | ```python
 162 | torch._inductor.aoti_compile_and_package()
 163 | torch._inductor.aoti_load_package()
 164 | ```
 165 | 
 166 | The new API stores device metadata in the package, so `aoti_load_package()` automatically uses the correct device type. You can only change the device *index* (e.g., cuda:0 vs cuda:1), not the device *type*.
 167 | 
 168 | ## Environment Variables Summary
 169 | 
 170 | | Variable | When | Purpose |
 171 | |----------|------|---------|
 172 | | `AOTI_RUNTIME_CHECK_INPUTS=1` | Compile time | Validate inputs match compilation guards |
 173 | | `TORCHINDUCTOR_NAN_ASSERTS=1` | Compile time | Check for NaN before/after kernels |
 174 | | `PYTORCH_NO_CUDA_MEMORY_CACHING=1` | Runtime | Make IMA errors deterministic |
 175 | | `CUDA_LAUNCH_BLOCKING=1` | Runtime | Force synchronous kernel launches |
 176 | | `AOT_INDUCTOR_DEBUG_INTERMEDIATE_VALUE_PRINTER=3` | Compile time | Print kernels at runtime |
 177 | | `TORCH_LOGS="+inductor,output_code"` | Runtime | See PT2 internal logs |
 178 | | `TORCH_SHOW_CPP_STACKTRACES=1` | Runtime | Show C++ stack traces |
```


---
## .claude/skills/aoti-debug/triton-index-out-of-bounds.md

```
   1 | # AOTI Triton Index Out of Bounds Debug Guide
   2 | 
   3 | This guide helps debug AOTI Triton kernel assertion errors with the `index out of bounds` pattern.
   4 | 
   5 | ## Error Pattern
   6 | 
   7 | This guide applies when you see errors like:
   8 | 
   9 | ```
  10 | /var/tmp/torchinductor_*/.../*.py:NN: unknown: block: [X,Y,Z], thread: [X,Y,Z]
  11 | Assertion `index out of bounds: 0 <= tmpN < ksM` failed.
  12 | ```
  13 | 
  14 | ### Key Information from Error
  15 | 
  16 | | Field | Value | Meaning |
  17 | |-------|-------|---------|
  18 | | File Path | `/var/tmp/torchinductor_*/*.py` | Generated Triton kernel file (runtime) |
  19 | | Line Number | `:NN` | Line in the generated kernel where assertion failed |
  20 | | Block/Thread | `[X,Y,Z]` | CUDA block and thread indices |
  21 | | Assertion | `0 <= tmpN < ksM` | Index `tmpN` must be within bounds `[0, ksM)` |
  22 | 
  23 | ### Understanding the Assertion
  24 | 
  25 | - `tmpN`: A computed index value in the Triton kernel
  26 | - `ksM`: A dynamic kernel size parameter (runtime value)
  27 | - The assertion fails when `tmpN < 0` or `tmpN >= ksM`
  28 | 
  29 | ---
  30 | 
  31 | ## Step 1: Collect AOTI Package
  32 | 
  33 | You need access to the AOTI package that was compiled. This is typically a `.pt2` package or extracted archive containing a `wrapper.cpp` file.
  34 | 
  35 | **Key File**: `*.wrapper.cpp` contains:
  36 | - All Triton kernel source code (embedded as comments)
  37 | - Kernel launch configurations
  38 | - Input/output tensor mappings
  39 | - Dynamic shape variable definitions
  40 | 
  41 | ---
  42 | 
  43 | ## Step 2: Locate the Failing Kernel in C++ Wrapper
  44 | 
  45 | ### Search for the Assertion Pattern
  46 | 
  47 | Extract the assertion pattern from the error (e.g., `tmp18 < ks0`) and search:
  48 | 
  49 | ```bash
  50 | # Search for the specific assertion
  51 | grep -n "tmpN < ksM" /path/to/*.wrapper.cpp
  52 | 
  53 | # Get context around the assertion (80 lines before, 20 after)
  54 | grep -n -B80 -A20 "tmpN < ksM" /path/to/*.wrapper.cpp
  55 | ```
  56 | 
  57 | ### Find the Full Kernel Definition
  58 | 
  59 | The kernel is embedded as a Python docstring comment in the C++ wrapper:
  60 | 
  61 | ```cpp
  62 |     /*
  63 |     async_compile.triton('triton_red_fused_...', '''
  64 |     import triton
  65 |     import triton.language as tl
  66 |     ...
  67 |     def triton_red_fused_...(in_ptr0, out_ptr1, ks0, xnumel, r0_numel, ...):
  68 | ```
  69 | 
  70 | ---
  71 | 
  72 | ## Step 3: Understand the Kernel Logic
  73 | 
  74 | Analyze the code path leading to the assertion. Common patterns that cause index out of bounds:
  75 | 
  76 | ### Pattern: Empty Tensor with ks0 = 0
  77 | 
  78 | When a dynamic shape `ks0 = 0`:
  79 | 1. `tmp13 = (-1) + 0 = -1`
  80 | 2. Index wrapping logic produces `-1`
  81 | 3. Assertion `0 <= -1 < 0` fails
  82 | 
  83 | ### Example Kernel Pattern
  84 | 
  85 | ```python
  86 | tmp13 = (-1) + ks0           # ks0 - 1
  87 | tmp14 = tl.where(tmp12, tmp10, tmp13)  # if condition: use tmp10, else: ks0-1
  88 | tmp15 = ks0
  89 | tmp16 = tmp14 + tmp15        # wrap-around for negative indices
  90 | tmp17 = tmp14 < 0
  91 | tmp18 = tl.where(tmp17, tmp16, tmp14)  # if negative: add ks0
  92 | 
  93 | # ASSERTION: 0 <= tmp18 < ks0
  94 | tl.device_assert(((0 <= tmp18) & (tmp18 < ks0)), "index out of bounds")
  95 | ```
  96 | 
  97 | ---
  98 | 
  99 | ## Step 4: Identify the Dynamic Shape Variable
 100 | 
 101 | ### Find Where the Kernel is Called
 102 | 
 103 | ```bash
 104 | grep -n "call_triton_KERNEL_NAME" /path/to/*.wrapper.cpp
 105 | ```
 106 | 
 107 | ### Example Output
 108 | 
 109 | ```cpp
 110 | call_triton_red_fused_...(arg1415_1, buf696, s607, 1L, s13, ...);
 111 | ```
 112 | 
 113 | ### Parameter Mapping
 114 | 
 115 | | Parameter | Value | Meaning |
 116 | |-----------|-------|---------|
 117 | | `in_ptr0` | `arg1415_1` | Input tensor |
 118 | | `out_ptr1` | `buf696` | Output buffer |
 119 | | `ks0` | `s607` | **Dynamic shape - this is the failing bound** |
 120 | 
 121 | ### Find the Definition of the Shape Variable
 122 | 
 123 | ```bash
 124 | grep -n "int64_t s607 = " /path/to/*.wrapper.cpp
 125 | ```
 126 | 
 127 | This shows which input tensor dimension defines the shape:
 128 | 
 129 | ```cpp
 130 | int64_t s607 = arg1416_1_size[0];
 131 | ```
 132 | 
 133 | ---
 134 | 
 135 | ## Step 5: Trace Back to Model Input
 136 | 
 137 | ### Find Input Index
 138 | 
 139 | Inputs are numbered sequentially. Find which input the argument corresponds to:
 140 | 
 141 | ```bash
 142 | grep -n 'inputs_info_\[INDEX\].name = "argNNN_1"' /path/to/*.wrapper.cpp
 143 | ```
 144 | 
 145 | ### Check Input Constraints
 146 | 
 147 | ```bash
 148 | grep -n "argNNN_1_size\[0\]" /path/to/*.wrapper.cpp
 149 | ```
 150 | 
 151 | Look for guards like:
 152 | ```cpp
 153 | if (arg_size[0] > 230400) {  // Upper bound check only - no lower bound!
 154 | ```
 155 | 
 156 | **Common Issue**: Upper bound checks exist but no lower bound checks for `>= 1`.
 157 | 
 158 | ---
 159 | 
 160 | ## Step 6: Map to Model Code
 161 | 
 162 | ### Use Source Node Comments
 163 | 
 164 | The C++ wrapper includes comments showing which PyTorch operations generated each kernel:
 165 | 
 166 | ```bash
 167 | grep -n -B5 "call_triton_KERNEL_NAME" /path/to/*.wrapper.cpp | grep "Source Nodes"
 168 | ```
 169 | 
 170 | ### Example Output
 171 | 
 172 | ```cpp
 173 | // Topologically Sorted Source Nodes: [slice_1, sub_89, cumsum, ge_231, where_2, index_copy]
 174 | ```
 175 | 
 176 | ### Map Operations to Python Code
 177 | 
 178 | | ATen Operation | Python Code Pattern |
 179 | |----------------|---------------------|
 180 | | `cumsum` | `torch.cumsum(tensor, dim=0)` |
 181 | | `sub` | `idx - 1` |
 182 | | `ge` | `idx >= 0` |
 183 | | `where` | `torch.where(condition, ...)` |
 184 | | `index_copy` | `tensor.index_copy(0, indices, source)` |
 185 | 
 186 | ---
 187 | 
 188 | ## Root Cause Analysis
 189 | 
 190 | ### Common Root Causes
 191 | 
 192 | 1. **Empty tensor at runtime**: A jagged/variable-length tensor has size 0 at runtime but wasn't tested during compilation
 193 | 2. **Missing lower bound guards**: AOTI only generates upper bound checks, not lower bound checks
 194 | 3. **Edge case not in sample inputs**: Sample inputs during AOTI export never included the edge case
 195 | 
 196 | ---
 197 | 
 198 | ## Fix Recommendations
 199 | 
 200 | ### Option 1: Add Guard in Forward Method
 201 | 
 202 | ```python
 203 | def forward(self, lengths: torch.Tensor, ...) -> torch.Tensor:
 204 |     if lengths.numel() == 0:
 205 |         device = lengths.device
 206 |         return torch.empty(0, self.output_dim, device=device)
 207 |     # ... rest of method
 208 | ```
 209 | 
 210 | ### Option 2: Fix the Specific Operation
 211 | 
 212 | Add handling for empty tensors in the problematic operation:
 213 | 
 214 | ```python
 215 | def process_events(self, lengths: torch.Tensor, ...):
 216 |     if lengths.numel() == 0:
 217 |         return torch.empty(0, self.emb_dim, device=lengths.device)
 218 |     # ... rest of method
 219 | ```
 220 | 
 221 | ### Option 3: Include Edge Cases in AOTI Export
 222 | 
 223 | Ensure sample inputs during AOTI export include:
 224 | - Empty tensors (size 0)
 225 | - Minimum size tensors (size 1)
 226 | - Maximum expected sizes
 227 | 
 228 | ---
 229 | 
 230 | ## Useful Commands Summary
 231 | 
 232 | ### Searching in AOTI Wrapper
 233 | 
 234 | ```bash
 235 | # Find kernel by assertion pattern
 236 | grep -n "tmpN < ksM" *.wrapper.cpp
 237 | 
 238 | # Get full kernel context
 239 | grep -n -B80 -A20 "ASSERTION_PATTERN" *.wrapper.cpp
 240 | 
 241 | # Find kernel call site
 242 | grep -n "call_KERNEL_NAME" *.wrapper.cpp
 243 | 
 244 | # Find dynamic shape definition
 245 | grep -n "int64_t SHAPE_VAR = " *.wrapper.cpp
 246 | 
 247 | # Find input mapping
 248 | grep -n 'inputs_info_\[INDEX\].name' *.wrapper.cpp
 249 | 
 250 | # Find size constraints
 251 | grep -n "SHAPE_VAR_size\[0\]" *.wrapper.cpp
 252 | ```
 253 | 
 254 | ### Environment Variables for Debugging
 255 | 
 256 | ```bash
 257 | # Enable debug output during torch.compile
 258 | export TORCH_COMPILE_DEBUG=1
 259 | 
 260 | # Save generated kernels to persistent location
 261 | export TORCHINDUCTOR_CACHE_DIR=/path/to/save/kernels
 262 | 
 263 | # Enable CUDA launch blocking for accurate stack traces
 264 | export CUDA_LAUNCH_BLOCKING=1
 265 | ```
```


---
## .claude/skills/at-dispatch-v2/SKILL.md

```
   1 | ---
   2 | name: at-dispatch-v2
   3 | description: Convert PyTorch AT_DISPATCH macros to AT_DISPATCH_V2 format in ATen C++ code. Use when porting AT_DISPATCH_ALL_TYPES_AND*, AT_DISPATCH_FLOATING_TYPES*, or other dispatch macros to the new v2 API. For ATen kernel files, CUDA kernels, and native operator implementations.
   4 | ---
   5 | 
   6 | # AT_DISPATCH to AT_DISPATCH_V2 Converter
   7 | 
   8 | This skill helps convert PyTorch's legacy AT_DISPATCH macros to the new AT_DISPATCH_V2 format, as defined in `aten/src/ATen/Dispatch_v2.h`.
   9 | 
  10 | ## When to use this skill
  11 | 
  12 | Use this skill when:
  13 | - Converting AT_DISPATCH_* macros to AT_DISPATCH_V2
  14 | - Porting ATen kernels to use the new dispatch API
  15 | - Working with files in `aten/src/ATen/native/` that use dispatch macros
  16 | - User mentions "AT_DISPATCH", "dispatch v2", "Dispatch_v2.h", or macro conversion
  17 | 
  18 | ## Quick reference
  19 | 
  20 | **Old format:**
  21 | ```cpp
  22 | AT_DISPATCH_ALL_TYPES_AND3(kBFloat16, kHalf, kBool, dtype, "kernel_name", [&]() {
  23 |   // lambda body
  24 | });
  25 | ```
  26 | 
  27 | **New format:**
  28 | ```cpp
  29 | AT_DISPATCH_V2(dtype, "kernel_name", AT_WRAP([&]() {
  30 |   // lambda body
  31 | }), AT_EXPAND(AT_ALL_TYPES), kBFloat16, kHalf, kBool);
  32 | ```
  33 | 
  34 | ## Key transformations
  35 | 
  36 | 1. **Reorder arguments**: `scalar_type` and `name` come first, then lambda, then types
  37 | 2. **Wrap the lambda**: Use `AT_WRAP(lambda)` to handle internal commas
  38 | 3. **Expand type groups**: Use `AT_EXPAND(AT_ALL_TYPES)` instead of implicit expansion
  39 | 4. **List individual types**: Add extra types (kHalf, kBFloat16, etc.) after expanded groups
  40 | 5. **Add include**: `#include <ATen/Dispatch_v2.h>` near other Dispatch includes
  41 | 
  42 | ## Instructions
  43 | 
  44 | ### Step 1: Add the Dispatch_v2.h include
  45 | 
  46 | Add the v2 header near the existing `#include <ATen/Dispatch.h>`:
  47 | 
  48 | ```cpp
  49 | #include <ATen/Dispatch.h>
  50 | #include <ATen/Dispatch_v2.h>
  51 | ```
  52 | 
  53 | Keep the old Dispatch.h include for now (other code may still need it).
  54 | 
  55 | ### Step 2: Identify the old dispatch pattern
  56 | 
  57 | Common patterns to convert:
  58 | 
  59 | - `AT_DISPATCH_ALL_TYPES_AND{2,3,4}(type1, type2, ..., scalar_type, name, lambda)`
  60 | - `AT_DISPATCH_FLOATING_TYPES_AND{2,3}(type1, type2, ..., scalar_type, name, lambda)`
  61 | - `AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND{2,3}(type1, ..., scalar_type, name, lambda)`
  62 | - `AT_DISPATCH_FLOATING_AND_COMPLEX_TYPES_AND{2,3}(type1, ..., scalar_type, name, lambda)`
  63 | 
  64 | ### Step 3: Map the old macro to type groups
  65 | 
  66 | Identify which type group macro corresponds to the base types:
  67 | 
  68 | | Old macro base | AT_DISPATCH_V2 type group |
  69 | |----------------|---------------------------|
  70 | | `ALL_TYPES` | `AT_EXPAND(AT_ALL_TYPES)` |
  71 | | `FLOATING_TYPES` | `AT_EXPAND(AT_FLOATING_TYPES)` |
  72 | | `INTEGRAL_TYPES` | `AT_EXPAND(AT_INTEGRAL_TYPES)` |
  73 | | `COMPLEX_TYPES` | `AT_EXPAND(AT_COMPLEX_TYPES)` |
  74 | | `ALL_TYPES_AND_COMPLEX` | `AT_EXPAND(AT_ALL_TYPES_AND_COMPLEX)` |
  75 | 
  76 | For combined patterns, use multiple `AT_EXPAND()` entries:
  77 | ```cpp
  78 | // Old: AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND2(...)
  79 | // New: AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_COMPLEX_TYPES), type1, type2
  80 | ```
  81 | 
  82 | ### Step 4: Extract the individual types
  83 | 
  84 | From `AT_DISPATCH_*_AND2(type1, type2, ...)` or `AT_DISPATCH_*_AND3(type1, type2, type3, ...)`, extract the individual types (type1, type2, etc.).
  85 | 
  86 | These become the trailing arguments after the type group:
  87 | ```cpp
  88 | AT_DISPATCH_V2(..., AT_EXPAND(AT_ALL_TYPES), kBFloat16, kHalf, kBool)
  89 |                                              ^^^^^^^^^^^^^^^^^^^^^^^^
  90 |                                              Individual types from AND3
  91 | ```
  92 | 
  93 | ### Step 5: Transform to AT_DISPATCH_V2
  94 | 
  95 | Apply the transformation:
  96 | 
  97 | **Pattern:**
  98 | ```cpp
  99 | AT_DISPATCH_V2(
 100 |   scalar_type,           // 1st: The dtype expression
 101 |   "name",                // 2nd: The debug string
 102 |   AT_WRAP(lambda),       // 3rd: The lambda wrapped in AT_WRAP
 103 |   type_groups,           // 4th+: Type groups with AT_EXPAND()
 104 |   individual_types       // Last: Individual types
 105 | )
 106 | ```
 107 | 
 108 | **Example transformation:**
 109 | ```cpp
 110 | // BEFORE
 111 | AT_DISPATCH_ALL_TYPES_AND3(
 112 |     kBFloat16, kHalf, kBool,
 113 |     iter.dtype(),
 114 |     "min_values_cuda",
 115 |     [&]() {
 116 |       min_values_kernel_cuda_impl<scalar_t>(iter);
 117 |     }
 118 | );
 119 | 
 120 | // AFTER
 121 | AT_DISPATCH_V2(
 122 |     iter.dtype(),
 123 |     "min_values_cuda",
 124 |     AT_WRAP([&]() {
 125 |       min_values_kernel_cuda_impl<scalar_t>(iter);
 126 |     }),
 127 |     AT_EXPAND(AT_ALL_TYPES),
 128 |     kBFloat16, kHalf, kBool
 129 | );
 130 | ```
 131 | 
 132 | ### Step 6: Handle multi-line lambdas
 133 | 
 134 | For lambdas with internal commas or complex expressions, AT_WRAP is essential:
 135 | 
 136 | ```cpp
 137 | AT_DISPATCH_V2(
 138 |     dtype,
 139 |     "complex_kernel",
 140 |     AT_WRAP([&]() {
 141 |       gpu_reduce_kernel<scalar_t, scalar_t>(
 142 |         iter,
 143 |         MinOps<scalar_t>{},
 144 |         thrust::pair<scalar_t, int64_t>(upper_bound(), 0)  // Commas inside!
 145 |       );
 146 |     }),
 147 |     AT_EXPAND(AT_ALL_TYPES)
 148 | );
 149 | ```
 150 | 
 151 | ### Step 7: Verify the conversion
 152 | 
 153 | Check that:
 154 | - [ ] `AT_WRAP()` wraps the entire lambda
 155 | - [ ] Type groups use `AT_EXPAND()`
 156 | - [ ] Individual types don't have `AT_EXPAND()` (just `kBFloat16`, not `AT_EXPAND(kBFloat16)`)
 157 | - [ ] Argument order is: scalar_type, name, lambda, types
 158 | - [ ] Include added: `#include <ATen/Dispatch_v2.h>`
 159 | 
 160 | ## Type group reference
 161 | 
 162 | Available type group macros (use with `AT_EXPAND()`):
 163 | 
 164 | ```cpp
 165 | AT_INTEGRAL_TYPES      // kByte, kChar, kInt, kLong, kShort
 166 | AT_FLOATING_TYPES      // kDouble, kFloat
 167 | AT_COMPLEX_TYPES       // kComplexDouble, kComplexFloat
 168 | AT_QINT_TYPES         // kQInt8, kQUInt8, kQInt32
 169 | AT_ALL_TYPES          // INTEGRAL_TYPES + FLOATING_TYPES
 170 | AT_ALL_TYPES_AND_COMPLEX  // ALL_TYPES + COMPLEX_TYPES
 171 | AT_INTEGRAL_TYPES_V2  // INTEGRAL_TYPES + unsigned types
 172 | AT_BAREBONES_UNSIGNED_TYPES  // kUInt16, kUInt32, kUInt64
 173 | AT_FLOAT8_TYPES       // Float8 variants
 174 | ```
 175 | 
 176 | ## Common patterns
 177 | 
 178 | ### Pattern: AT_DISPATCH_ALL_TYPES_AND2
 179 | 
 180 | ```cpp
 181 | // Before
 182 | AT_DISPATCH_ALL_TYPES_AND2(kHalf, kBFloat16, dtype, "op", [&]() {
 183 |   kernel<scalar_t>(data);
 184 | });
 185 | 
 186 | // After
 187 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
 188 |   kernel<scalar_t>(data);
 189 | }), AT_EXPAND(AT_ALL_TYPES), kHalf, kBFloat16);
 190 | ```
 191 | 
 192 | ### Pattern: AT_DISPATCH_FLOATING_TYPES_AND3
 193 | 
 194 | ```cpp
 195 | // Before
 196 | AT_DISPATCH_FLOATING_TYPES_AND3(kHalf, kBFloat16, kFloat8_e4m3fn,
 197 |     tensor.scalar_type(), "float_op", [&] {
 198 |   process<scalar_t>(tensor);
 199 | });
 200 | 
 201 | // After
 202 | AT_DISPATCH_V2(tensor.scalar_type(), "float_op", AT_WRAP([&] {
 203 |   process<scalar_t>(tensor);
 204 | }), AT_EXPAND(AT_FLOATING_TYPES), kHalf, kBFloat16, kFloat8_e4m3fn);
 205 | ```
 206 | 
 207 | ### Pattern: AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND2
 208 | 
 209 | ```cpp
 210 | // Before
 211 | AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND2(
 212 |     kComplexHalf, kHalf,
 213 |     self.scalar_type(),
 214 |     "complex_op",
 215 |     [&] {
 216 |       result = compute<scalar_t>(self);
 217 |     }
 218 | );
 219 | 
 220 | // After
 221 | AT_DISPATCH_V2(
 222 |     self.scalar_type(),
 223 |     "complex_op",
 224 |     AT_WRAP([&] {
 225 |       result = compute<scalar_t>(self);
 226 |     }),
 227 |     AT_EXPAND(AT_ALL_TYPES),
 228 |     AT_EXPAND(AT_COMPLEX_TYPES),
 229 |     kComplexHalf,
 230 |     kHalf
 231 | );
 232 | ```
 233 | 
 234 | ## Edge cases
 235 | 
 236 | ### Case 1: No extra types (rare)
 237 | 
 238 | ```cpp
 239 | // Before
 240 | AT_DISPATCH_ALL_TYPES(dtype, "op", [&]() { kernel<scalar_t>(); });
 241 | 
 242 | // After
 243 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
 244 |   kernel<scalar_t>();
 245 | }), AT_EXPAND(AT_ALL_TYPES));
 246 | ```
 247 | 
 248 | ### Case 2: Many individual types (AND4, AND5, etc.)
 249 | 
 250 | ```cpp
 251 | // Before
 252 | AT_DISPATCH_FLOATING_TYPES_AND4(kHalf, kBFloat16, kFloat8_e4m3fn, kFloat8_e5m2,
 253 |     dtype, "float8_op", [&]() { kernel<scalar_t>(); });
 254 | 
 255 | // After
 256 | AT_DISPATCH_V2(dtype, "float8_op", AT_WRAP([&]() {
 257 |   kernel<scalar_t>();
 258 | }), AT_EXPAND(AT_FLOATING_TYPES), kHalf, kBFloat16, kFloat8_e4m3fn, kFloat8_e5m2);
 259 | ```
 260 | 
 261 | ### Case 3: Lambda with no captures
 262 | 
 263 | ```cpp
 264 | // Before
 265 | AT_DISPATCH_ALL_TYPES_AND2(kHalf, kBool, dtype, "op", []() {
 266 |   static_kernel<scalar_t>();
 267 | });
 268 | 
 269 | // After
 270 | AT_DISPATCH_V2(dtype, "op", AT_WRAP([]() {
 271 |   static_kernel<scalar_t>();
 272 | }), AT_EXPAND(AT_ALL_TYPES), kHalf, kBool);
 273 | ```
 274 | 
 275 | ## Benefits of AT_DISPATCH_V2
 276 | 
 277 | 1. **No arity in macro name**: Don't need different macros for AND2, AND3, AND4
 278 | 2. **Composable type sets**: Mix and match type groups with `AT_EXPAND()`
 279 | 3. **Extensible**: Easy to add more types without hitting macro limits
 280 | 4. **Clearer**: Type groups are explicit, not implicit in macro name
 281 | 
 282 | ## Important notes
 283 | 
 284 | - Keep `#include <ATen/Dispatch.h>` - other code may need it
 285 | - The `AT_WRAP()` is mandatory - prevents comma parsing issues in the lambda
 286 | - Type groups need `AT_EXPAND()`, individual types don't
 287 | - The v2 API is in `aten/src/ATen/Dispatch_v2.h` - refer to it for full docs
 288 | - See the header file for the Python script to regenerate the macro implementation
 289 | 
 290 | ## Workflow
 291 | 
 292 | When asked to convert AT_DISPATCH macros:
 293 | 
 294 | 1. Read the file to identify all AT_DISPATCH uses
 295 | 2. Add `#include <ATen/Dispatch_v2.h>` if not present
 296 | 3. For each dispatch macro:
 297 |    - Identify the pattern and extract components
 298 |    - Map the base type group
 299 |    - Extract individual types
 300 |    - Construct the AT_DISPATCH_V2 call
 301 |    - Apply with Edit tool
 302 | 4. Show the user the complete converted file
 303 | 5. Explain what was changed
 304 | 
 305 | Do NOT compile or test the code - focus on accurate conversion only.
```


---
## .claude/skills/docstring/SKILL.md

```
   1 | ---
   2 | name: docstring
   3 | description: Write docstrings for PyTorch functions and methods following PyTorch conventions. Use when writing or updating docstrings in PyTorch code.
   4 | ---
   5 | 
   6 | # PyTorch Docstring Writing Guide
   7 | 
   8 | This skill describes how to write docstrings for functions and methods in the PyTorch project, following the conventions in `torch/_tensor_docs.py` and `torch/nn/functional.py`.
   9 | 
  10 | ## General Principles
  11 | 
  12 | - Use **raw strings** (`r"""..."""`) for all docstrings to avoid issues with LaTeX/math backslashes
  13 | - Follow **Sphinx/reStructuredText** (reST) format for documentation
  14 | - Be **concise but complete** - include all essential information
  15 | - Always include **examples** when possible
  16 | - Use **cross-references** to related functions/classes
  17 | 
  18 | ## Docstring Structure
  19 | 
  20 | ### 1. Function Signature (First Line)
  21 | 
  22 | Start with the function signature showing all parameters:
  23 | 
  24 | ```python
  25 | r"""function_name(param1, param2, *, kwarg1=default1, kwarg2=default2) -> ReturnType
  26 | ```
  27 | 
  28 | **Notes:**
  29 | - Include the function name
  30 | - Show positional and keyword-only arguments (use `*` separator)
  31 | - Include default values
  32 | - Show return type annotation
  33 | - This line should NOT end with a period
  34 | 
  35 | ### 2. Brief Description
  36 | 
  37 | Provide a one-line description of what the function does:
  38 | 
  39 | ```python
  40 | r"""conv2d(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1) -> Tensor
  41 | 
  42 | Applies a 2D convolution over an input image composed of several input
  43 | planes.
  44 | ```
  45 | 
  46 | ### 3. Mathematical Formulas (if applicable)
  47 | 
  48 | Use Sphinx math directives for mathematical expressions:
  49 | 
  50 | ```python
  51 | .. math::
  52 |     \text{Softmax}(x_{i}) = \frac{\exp(x_i)}{\sum_j \exp(x_j)}
  53 | ```
  54 | 
  55 | Or inline math: `:math:\`x^2\``
  56 | 
  57 | ### 4. Cross-References
  58 | 
  59 | Link to related classes and functions using Sphinx roles:
  60 | 
  61 | - `:class:\`~torch.nn.ModuleName\`` - Link to a class
  62 | - `:func:\`torch.function_name\`` - Link to a function
  63 | - `:meth:\`~Tensor.method_name\`` - Link to a method
  64 | - `:attr:\`attribute_name\`` - Reference an attribute
  65 | - The `~` prefix shows only the last component (e.g., `Conv2d` instead of `torch.nn.Conv2d`)
  66 | 
  67 | **Example:**
  68 | ```python
  69 | See :class:`~torch.nn.Conv2d` for details and output shape.
  70 | ```
  71 | 
  72 | ### 5. Notes and Warnings
  73 | 
  74 | Use admonitions for important information:
  75 | 
  76 | ```python
  77 | .. note::
  78 |     This function doesn't work directly with NLLLoss,
  79 |     which expects the Log to be computed between the Softmax and itself.
  80 |     Use log_softmax instead (it's faster and has better numerical properties).
  81 | 
  82 | .. warning::
  83 |     :func:`new_tensor` always copies :attr:`data`. If you have a Tensor
  84 |     ``data`` and want to avoid a copy, use :func:`torch.Tensor.requires_grad_`
  85 |     or :func:`torch.Tensor.detach`.
  86 | ```
  87 | 
  88 | ### 6. Args Section
  89 | 
  90 | Document all parameters with type annotations and descriptions:
  91 | 
  92 | ```python
  93 | Args:
  94 |     input (Tensor): input tensor of shape :math:`(\text{minibatch} , \text{in\_channels} , iH , iW)`
  95 |     weight (Tensor): filters of shape :math:`(\text{out\_channels} , kH , kW)`
  96 |     bias (Tensor, optional): optional bias tensor of shape :math:`(\text{out\_channels})`. Default: ``None``
  97 |     stride (int or tuple): the stride of the convolving kernel. Can be a single number or a
  98 |       tuple `(sH, sW)`. Default: 1
  99 | ```
 100 | 
 101 | **Formatting rules:**
 102 | - Parameter name in **lowercase**
 103 | - Type in parentheses: `(Type)`, `(Type, optional)` for optional parameters
 104 | - Description follows the type
 105 | - For optional parameters, include "Default: ``value``" at the end
 106 | - Use double backticks for inline code: ``` ``None`` ```
 107 | - Indent continuation lines by 2 spaces
 108 | 
 109 | ### 7. Keyword Args Section (if applicable)
 110 | 
 111 | Sometimes keyword arguments are documented separately:
 112 | 
 113 | ```python
 114 | Keyword args:
 115 |     dtype (:class:`torch.dtype`, optional): the desired type of returned tensor.
 116 |         Default: if None, same :class:`torch.dtype` as this tensor.
 117 |     device (:class:`torch.device`, optional): the desired device of returned tensor.
 118 |         Default: if None, same :class:`torch.device` as this tensor.
 119 |     requires_grad (bool, optional): If autograd should record operations on the
 120 |         returned tensor. Default: ``False``.
 121 | ```
 122 | 
 123 | ### 8. Returns Section (if needed)
 124 | 
 125 | Document the return value:
 126 | 
 127 | ```python
 128 | Returns:
 129 |     Tensor: Sampled tensor of same shape as `logits` from the Gumbel-Softmax distribution.
 130 |         If ``hard=True``, the returned samples will be one-hot, otherwise they will
 131 |         be probability distributions that sum to 1 across `dim`.
 132 | ```
 133 | 
 134 | Or simply include it in the function signature line if obvious from context.
 135 | 
 136 | ### 9. Examples Section
 137 | 
 138 | Always include examples when possible:
 139 | 
 140 | ```python
 141 | Examples::
 142 | 
 143 |     >>> inputs = torch.randn(33, 16, 30)
 144 |     >>> filters = torch.randn(20, 16, 5)
 145 |     >>> F.conv1d(inputs, filters)
 146 | 
 147 |     >>> # With square kernels and equal stride
 148 |     >>> filters = torch.randn(8, 4, 3, 3)
 149 |     >>> inputs = torch.randn(1, 4, 5, 5)
 150 |     >>> F.conv2d(inputs, filters, padding=1)
 151 | ```
 152 | 
 153 | **Formatting rules:**
 154 | - Use `Examples::` with double colon
 155 | - Use `>>>` prompt for Python code
 156 | - Include comments with `#` when helpful
 157 | - Show actual output when it helps understanding (indent without `>>>`)
 158 | 
 159 | ### 10. External References
 160 | 
 161 | Link to papers or external documentation:
 162 | 
 163 | ```python
 164 | .. _Link Name:
 165 |     https://arxiv.org/abs/1611.00712
 166 | ```
 167 | 
 168 | Reference them in text: ```See `Link Name`_```
 169 | 
 170 | ## Method Types
 171 | 
 172 | ### Native Python Functions
 173 | 
 174 | For regular Python functions, use a standard docstring:
 175 | 
 176 | ```python
 177 | def relu(input: Tensor, inplace: bool = False) -> Tensor:
 178 |     r"""relu(input, inplace=False) -> Tensor
 179 | 
 180 |     Applies the rectified linear unit function element-wise. See
 181 |     :class:`~torch.nn.ReLU` for more details.
 182 |     """
 183 |     # implementation
 184 | ```
 185 | 
 186 | ### C-Bound Functions (using add_docstr)
 187 | 
 188 | For C-bound functions, use `_add_docstr`:
 189 | 
 190 | ```python
 191 | conv1d = _add_docstr(
 192 |     torch.conv1d,
 193 |     r"""
 194 | conv1d(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1) -> Tensor
 195 | 
 196 | Applies a 1D convolution over an input signal composed of several input
 197 | planes.
 198 | 
 199 | See :class:`~torch.nn.Conv1d` for details and output shape.
 200 | 
 201 | Args:
 202 |     input: input tensor of shape :math:`(\text{minibatch} , \text{in\_channels} , iW)`
 203 |     weight: filters of shape :math:`(\text{out\_channels} , kW)`
 204 |     ...
 205 | """,
 206 | )
 207 | ```
 208 | 
 209 | ### In-Place Variants
 210 | 
 211 | For in-place operations (ending with `_`), reference the original:
 212 | 
 213 | ```python
 214 | add_docstr_all(
 215 |     "abs_",
 216 |     r"""
 217 | abs_() -> Tensor
 218 | 
 219 | In-place version of :meth:`~Tensor.abs`
 220 | """,
 221 | )
 222 | ```
 223 | 
 224 | ### Alias Functions
 225 | 
 226 | For aliases, simply reference the original:
 227 | 
 228 | ```python
 229 | add_docstr_all(
 230 |     "absolute",
 231 |     r"""
 232 | absolute() -> Tensor
 233 | 
 234 | Alias for :func:`abs`
 235 | """,
 236 | )
 237 | ```
 238 | 
 239 | ## Common Patterns
 240 | 
 241 | ### Shape Documentation
 242 | 
 243 | Use LaTeX math notation for tensor shapes:
 244 | 
 245 | ```python
 246 | :math:`(\text{minibatch} , \text{in\_channels} , iH , iW)`
 247 | ```
 248 | 
 249 | ### Reusable Argument Definitions
 250 | 
 251 | For commonly used arguments, define them once and reuse:
 252 | 
 253 | ```python
 254 | common_args = parse_kwargs(
 255 |     """
 256 |     dtype (:class:`torch.dtype`, optional): the desired type of returned tensor.
 257 |         Default: if None, same as this tensor.
 258 | """
 259 | )
 260 | 
 261 | # Then use with .format():
 262 | r"""
 263 | ...
 264 | 
 265 | Keyword args:
 266 |     {dtype}
 267 |     {device}
 268 | """.format(**common_args)
 269 | ```
 270 | 
 271 | ### Template Insertion
 272 | 
 273 | Insert reproducibility notes or other common text:
 274 | 
 275 | ```python
 276 | r"""
 277 | {tf32_note}
 278 | 
 279 | {cudnn_reproducibility_note}
 280 | """.format(**reproducibility_notes, **tf32_notes)
 281 | ```
 282 | 
 283 | ## Complete Example
 284 | 
 285 | Here's a complete example showing all elements:
 286 | 
 287 | ```python
 288 | def gumbel_softmax(
 289 |     logits: Tensor,
 290 |     tau: float = 1,
 291 |     hard: bool = False,
 292 |     eps: float = 1e-10,
 293 |     dim: int = -1,
 294 | ) -> Tensor:
 295 |     r"""
 296 |     Sample from the Gumbel-Softmax distribution and optionally discretize.
 297 | 
 298 |     Args:
 299 |         logits (Tensor): `[..., num_features]` unnormalized log probabilities
 300 |         tau (float): non-negative scalar temperature
 301 |         hard (bool): if ``True``, the returned samples will be discretized as one-hot vectors,
 302 |               but will be differentiated as if it is the soft sample in autograd. Default: ``False``
 303 |         dim (int): A dimension along which softmax will be computed. Default: -1
 304 | 
 305 |     Returns:
 306 |         Tensor: Sampled tensor of same shape as `logits` from the Gumbel-Softmax distribution.
 307 |             If ``hard=True``, the returned samples will be one-hot, otherwise they will
 308 |             be probability distributions that sum to 1 across `dim`.
 309 | 
 310 |     .. note::
 311 |         This function is here for legacy reasons, may be removed from nn.Functional in the future.
 312 | 
 313 |     Examples::
 314 |         >>> logits = torch.randn(20, 32)
 315 |         >>> # Sample soft categorical using reparametrization trick:
 316 |         >>> F.gumbel_softmax(logits, tau=1, hard=False)
 317 |         >>> # Sample hard categorical using "Straight-through" trick:
 318 |         >>> F.gumbel_softmax(logits, tau=1, hard=True)
 319 | 
 320 |     .. _Link 1:
 321 |         https://arxiv.org/abs/1611.00712
 322 |     """
 323 |     # implementation
 324 | ```
 325 | 
 326 | ## Quick Checklist
 327 | 
 328 | When writing a PyTorch docstring, ensure:
 329 | 
 330 | - [ ] Use raw string (`r"""`)
 331 | - [ ] Include function signature on first line
 332 | - [ ] Provide brief description
 333 | - [ ] Document all parameters in Args section with types
 334 | - [ ] Include default values for optional parameters
 335 | - [ ] Use Sphinx cross-references (`:func:`, `:class:`, `:meth:`)
 336 | - [ ] Add mathematical formulas if applicable
 337 | - [ ] Include at least one example in Examples section
 338 | - [ ] Add warnings/notes for important caveats
 339 | - [ ] Link to related module class with `:class:`
 340 | - [ ] Use proper math notation for tensor shapes
 341 | - [ ] Follow consistent formatting and indentation
 342 | 
 343 | ## Common Sphinx Roles Reference
 344 | 
 345 | - `:class:\`~torch.nn.Module\`` - Class reference
 346 | - `:func:\`torch.function\`` - Function reference
 347 | - `:meth:\`~Tensor.method\`` - Method reference
 348 | - `:attr:\`attribute\`` - Attribute reference
 349 | - `:math:\`equation\`` - Inline math
 350 | - `:ref:\`label\`` - Internal reference
 351 | - ``` ``code`` ``` - Inline code (use double backticks)
 352 | 
 353 | ## Additional Notes
 354 | 
 355 | - **Indentation**: Use 4 spaces for code, 2 spaces for continuation of parameter descriptions
 356 | - **Line length**: Try to keep lines under 100 characters when possible
 357 | - **Periods**: End sentences with periods, but not the signature line
 358 | - **Backticks**: Use double backticks for code: ``` ``True`` ``None`` ``False`` ```
 359 | - **Types**: Common types are `Tensor`, `int`, `float`, `bool`, `str`, `tuple`, `list`, etc.
```


---
## .claude/skills/document-public-apis/SKILL.md

```
   1 | ---
   2 | name: document-public-apis
   3 | description: Document undocumented public APIs in PyTorch by removing functions from coverage_ignore_functions and coverage_ignore_classes in docs/source/conf.py, running Sphinx coverage, and adding the appropriate autodoc directives to the correct .md or .rst doc files. Use when a user asks to remove functions from conf.py ignore lists.
   4 | ---
   5 | 
   6 | # Document Public APIs
   7 | 
   8 | This skill documents undocumented public APIs in PyTorch by removing entries from the coverage ignore lists in `docs/source/conf.py` and adding Sphinx autodoc directives (e.g., `autosummary`, `currentmodule`, `autoclass`, `automodule`) to the corresponding `.md` or `.rst` doc source files in `docs/source/`.
   9 | 
  10 | **"Documenting" means adding autodoc directives to doc source files — NEVER modifying Python source code.** Do not add or edit docstrings in `.py` files. Do not read or inspect Python source files. Sphinx will pull whatever docstring exists (or render an empty entry if none exists). Your only job is to add the correct directive to the correct doc file.
  11 | 
  12 | ## Overview
  13 | 
  14 | `docs/source/conf.py` contains two lists that suppress Sphinx coverage warnings for undocumented APIs:
  15 | 
  16 | - `coverage_ignore_functions`: undocumented functions
  17 | - `coverage_ignore_classes`: undocumented classes
  18 | 
  19 | Entries are organized by **module comment groups**. Each group has a module label comment followed by the function/class names that belong to that module:
  20 | 
  21 | ```python
  22 | coverage_ignore_functions = [
  23 |     # torch.ao.quantization.fx.convert              <-- module label comment
  24 |     "convert",                                       # <-- entries belonging to this module
  25 |     "convert_custom_module",
  26 |     "convert_standalone_module",
  27 |     "convert_weighted_module",
  28 |     # torch.ao.quantization.fx.fuse                 <-- next module group
  29 |     "fuse",
  30 |     # torch.nn.functional
  31 |     "assert_int_or_pair",  # looks unintentionally public   <-- entry with inline comment
  32 |     "constant",  # deprecated                                <-- entry with inline comment
  33 | ]
  34 | ```
  35 | 
  36 | There are two kinds of comments:
  37 | - **Module label comments** (`# torch.ao.quantization.fx.convert`): these label which module the entries below belong to. They appear on their own line before a group of entries.
  38 | - **Inline comments** (`# deprecated`, `# documented as adaptive_max_pool1d`): these appear after a string entry on the same line and explain *why* the entry is in the ignore list.
  39 | 
  40 | The module label comment directly tells you:
  41 | 1. Which module the functions belong to
  42 | 2. Where to add them in the docs (e.g., `# torch.ao.quantization.fx.convert` → the functions go under `torch.ao.quantization.fx.convert` in the doc file)
  43 | 
  44 | ## Instructions
  45 | 
  46 | Each invocation of this skill processes **one batch** of module groups. Pick one or more complete module groups from the ignore lists, document their functions, and verify.
  47 | 
  48 | ### Step 1: Select module groups to document
  49 | 
  50 | Read `docs/source/conf.py` and select one or more **complete module groups** to document. A module group is a module label comment and all entries beneath it up to the next module label comment. Process entire groups — never split a group across batches.
  51 | 
  52 | For example, selecting the `torch.ao.quantization.fx.convert` group means taking all of:
  53 | 
  54 | ```python
  55 | # torch.ao.quantization.fx.convert
  56 | "convert",
  57 | "convert_custom_module",
  58 | "convert_standalone_module",
  59 | "convert_weighted_module",
  60 | ```
  61 | 
  62 | Work through the lists top-to-bottom. Choose enough groups to make meaningful progress (aim for 5–15 functions total, but always include complete groups even if that means going slightly over).
  63 | 
  64 | **Check inline comments before including an entry.** Some entries have inline comments that indicate they should not be documented:
  65 | 
  66 | - `# deprecated` — The function is deprecated. Leave it in the ignore list.
  67 | - `# documented as <other_name>` — Already documented under a different name. Leave it.
  68 | - `# looks unintentionally public` — Probably not meant to be public API. Leave it.
  69 | - `# legacy helper for ...` — Same as deprecated. Leave it.
  70 | - `# utility function` - Leave it.
  71 | 
  72 | If a module group has a **mix** of regular entries and entries with inline comments, still process the group — but only comment out the regular entries. Leave entries with inline comments untouched in the ignore list.
  73 | 
  74 | ### Step 2: Present the batch to the user
  75 | 
  76 | **Before making any edits**, present the selected module groups and their functions to the user. Show them organized by module:
  77 | 
  78 | ```
  79 | Module: torch.ao.quantization.fx.convert
  80 |   - convert
  81 |   - convert_custom_module
  82 |   - convert_standalone_module
  83 |   - convert_weighted_module
  84 | 
  85 | Module: torch.ao.quantization.fx.fuse
  86 |   - fuse
  87 | ```
  88 | 
  89 | Then use the `AskUserQuestion` tool to let the user confirm, with options like:
  90 | - "Proceed with this batch"
  91 | - "Skip some entries" (user can specify which to remove)
  92 | - "Pick a different batch"
  93 | 
  94 | ### Step 3: Comment out entries in conf.py
  95 | 
  96 | After the user confirms, edit `docs/source/conf.py` and **comment out** (do not delete) the selected entries. Use a `#` prefix on each string entry line:
  97 | 
  98 | ```python
  99 | # torch.ao.quantization.fx.convert
 100 | # "convert",
 101 | # "convert_custom_module",
 102 | # "convert_standalone_module",
 103 | # "convert_weighted_module",
 104 | ```
 105 | 
 106 | This preserves the original entries so they can be restored if verification fails.
 107 | 
 108 | ### Step 4: Run Sphinx coverage
 109 | 
 110 | ```bash
 111 | cd docs && make coverage
 112 | ```
 113 | 
 114 | **Ignore the terminal output of `make coverage`.** It often contains unrelated tracebacks and errors from Sphinx extensions (e.g., `onnx_ir`, `katex`, `sphinxcontrib`) that have nothing to do with coverage. The only thing that matters is whether `docs/build/coverage/python.txt` was generated. Read that file to see the specific undocumented APIs.
 115 | 
 116 | The format of `python.txt` lists each undocumented API as:
 117 | 
 118 | ```
 119 | torch.ao.quantization.fx.convert
 120 |    * convert
 121 |    * convert_custom_module
 122 |    * convert_standalone_module
 123 |    * convert_weighted_module
 124 | ```
 125 | 
 126 | **Not all commented-out functions will appear in `python.txt`.** Some may already be documented elsewhere. This is fine — only add directives for functions that actually appear in `python.txt`.
 127 | 
 128 | If `make coverage` fails due to missing dependencies, first run:
 129 | 
 130 | ```bash
 131 | cd docs && pip install -r requirements.txt
 132 | ```
 133 | 
 134 | ### Step 5: Add documentation directives
 135 | 
 136 | For each function listed in `python.txt`, use the **module label comment** from `conf.py` to determine where it should be added. The module comment gives you the full module path, which maps to a doc source file and a section within that file.
 137 | 
 138 | #### Finding the correct doc file
 139 | 
 140 | The module comment maps to a doc source file in `docs/source/`. When unsure, search for other functions from the same module:
 141 | 
 142 | ```bash
 143 | grep -rn "torch.module_name" docs/source/*.md docs/source/*.rst
 144 | ```
 145 | 
 146 | Or list candidate files:
 147 | 
 148 | ```bash
 149 | ls docs/source/*module_name*
 150 | ```
 151 | 
 152 | If no doc file exists for a submodule, check whether a parent module's doc file has a section for it (e.g., `backends.md` has sections for `torch.backends.cuda`, `torch.backends.cudnn`, etc.). If not, add a new section to the parent file following existing patterns.
 153 | 
 154 | #### Adding the directives
 155 | 
 156 | **Read the target doc file first** and match the exact patterns already used there. Do not invent new patterns or use bare `autofunction` with fully qualified names — always use the proper hierarchical structure with `automodule`, `currentmodule`, and short names. Do not use `. py:module::` since that just suppresses errors and doesn't actually document the function. Look at other files that match the target file's format (e.g., `.md` vs. `.rst`) under `docs/source/` to see examples.
 157 | 
 158 | There are two file formats. Match the one used in the target file.
 159 | 
 160 | **Pattern A — MyST Markdown files (`.md`):** Used in files like `accelerator.md`, `backends.md`, `cuda.md`.
 161 | 
 162 | The hierarchical structure uses `automodule` to register the module, `currentmodule` to set context, then short names:
 163 | 
 164 | ```markdown
 165 | ## torch.ao.quantization.fx.convert
 166 | 
 167 | ```{eval-rst}
 168 | .. automodule:: torch.ao.quantization.fx.convert
 169 | ```
 170 | 
 171 | ```{eval-rst}
 172 | .. currentmodule:: torch.ao.quantization.fx.convert
 173 | ```
 174 | 
 175 | ```{eval-rst}
 176 | .. autofunction:: convert
 177 | ```
 178 | 
 179 | ```{eval-rst}
 180 | .. autofunction:: convert_custom_module
 181 | ```
 182 | ```
 183 | 
 184 | For `autosummary` blocks (used in some files instead of individual directives):
 185 | 
 186 | ```markdown
 187 | ```{eval-rst}
 188 | .. autosummary::
 189 |     :toctree: generated
 190 |     :nosignatures:
 191 | 
 192 |     existing_function
 193 |     your_new_function
 194 | `` `
 195 | ```
 196 | 
 197 | For classes:
 198 | 
 199 | ```markdown
 200 | ```{eval-rst}
 201 | .. autoclass:: YourClass
 202 |     :members:
 203 | `` `
 204 | ```
 205 | 
 206 | **Pattern B — reStructuredText files (`.rst`):** Used in files like `torch.rst`, `nn.rst`.
 207 | 
 208 | Same hierarchical structure without the markdown fences:
 209 | 
 210 | ```rst
 211 | torch.ao.quantization.fx.convert
 212 | ---------------------------------
 213 | 
 214 | .. automodule:: torch.ao.quantization.fx.convert
 215 | 
 216 | .. currentmodule:: torch.ao.quantization.fx.convert
 217 | 
 218 | .. autosummary::
 219 |     :toctree: generated
 220 |     :nosignatures:
 221 | 
 222 |     convert
 223 |     convert_custom_module
 224 |     convert_standalone_module
 225 |     convert_weighted_module
 226 | ```
 227 | 
 228 | For individual directives:
 229 | 
 230 | ```rst
 231 | .. automodule:: torch.submodule
 232 | 
 233 | .. currentmodule:: torch.submodule
 234 | 
 235 | .. autofunction:: function_name
 236 | 
 237 | .. autoclass:: ClassName
 238 |     :members:
 239 | ```
 240 | 
 241 | **Key rules:**
 242 | - The module label comment from `conf.py` (e.g., `# torch.ao.quantization.fx.convert`) tells you exactly which `automodule` and `currentmodule` to use.
 243 | - Always set `.. automodule::` and `.. currentmodule::` before documenting functions from a module.
 244 | - Use **short names** (e.g., `convert`, not `torch.ao.quantization.fx.convert.convert`) after `currentmodule` is set.
 245 | - If the module already has an `automodule`/`currentmodule` in the file, don't add another — just add your function under the existing one.
 246 | - Match whichever style the file already uses (`autosummary` blocks vs. individual `autofunction` directives).
 247 | 
 248 | #### Placing in the right section
 249 | 
 250 | Read the target doc file and find the appropriate section. If the module already has a section (e.g., `## torch.backends.cuda` in `backends.md`), add the functions there. If no section exists yet, create one following the existing section patterns in the file. Group all functions from the same module group together.
 251 | 
 252 | ### Step 6: Verify with coverage
 253 | 
 254 | Run coverage again:
 255 | 
 256 | ```bash
 257 | cd docs && make coverage
 258 | ```
 259 | 
 260 | Ignore the terminal output — only read `docs/build/coverage/python.txt`. Verification passes when `python.txt` contains **zero undocumented functions across ALL modules**. It should only have the statistics table with 100% coverage and 0 undocumented for every module. For example:
 261 | 
 262 | ```
 263 | Undocumented Python objects
 264 | ===========================
 265 | 
 266 | Statistics
 267 | ----------
 268 | 
 269 | +---------------------------+----------+--------------+
 270 | | Module                    | Coverage | Undocumented |
 271 | +===========================+==========+==============+
 272 | | torch                     | 100.00%  | 0            |
 273 | +---------------------------+----------+--------------+
 274 | | torch.accelerator         | 100.00%  | 0            |
 275 | +---------------------------+----------+--------------+
 276 | ```
 277 | 
 278 | If any module shows undocumented functions (coverage below 100% or undocumented count > 0), verification has failed.
 279 | 
 280 | **If verification succeeds (zero undocumented across all modules):** Go to Step 7.
 281 | 
 282 | **If verification fails (any undocumented functions remain):** Read `docs/build/coverage/python.txt` to see which functions are still listed as undocumented. Common issues include:
 283 | 
 284 | - Wrong doc file: the function was added to the wrong `.md`/`.rst` file. Move the directive to the correct file.
 285 | - Wrong directive type: e.g., used `autofunction` for a class, or `autoclass` for a function. Fix the directive.
 286 | - Wrong module path in the directive: e.g., `torch.foo.bar` should be `torch.foo.baz.bar`. Correct the qualified name.
 287 | - Function added to an `autosummary` block with the wrong `currentmodule`: make sure the `.. currentmodule::` directive above the block matches.
 288 | - Missing `automodule` for a submodule that hasn't been registered yet. Add a `.. automodule:: torch.submodule` directive before documenting functions from that submodule.
 289 | 
 290 | Fix the doc directive based on the error, then re-run `make coverage`. Repeat until verification passes.
 291 | 
 292 | If a function still fails after multiple attempts, **stop and show the error to the user.** Present the function name and the error, then use the `AskUserQuestion` tool with options like:
 293 | - "Uncomment it to restore to ignore list (skip for now)"
 294 | - "Try a different approach"
 295 | - "Investigate further"
 296 | 
 297 | ### Step 7: Report progress
 298 | 
 299 | **Present a progress summary to the user** showing:
 300 | 
 301 | - Which module groups were processed and how many functions were documented
 302 | - Which functions were skipped or restored to the ignore list (and why)
 303 | - How many entries remain in `coverage_ignore_functions` and `coverage_ignore_classes`
 304 | 
 305 | ### Step 8: Clean up commented-out entries in conf.py
 306 | 
 307 | Now that verification has passed, delete the commented-out string entries from Step 3. These are lines that start with `# "` inside `coverage_ignore_functions` and `coverage_ignore_classes`. Commented-out string entries always contain **quotes** — that's how you distinguish them from module label comments:
 308 | 
 309 | ```python
 310 | # "disable_global_flags",       <-- commented-out string entry (has quotes) → DELETE
 311 | # torch.backends                <-- module label comment (no quotes) → KEEP if it has active entries
 312 | ```
 313 | 
 314 | Also delete any module label comments that no longer have active entries beneath them (i.e., all their entries were either commented out and now deleted, or had inline comments and were left in place but the module label is otherwise empty).
 315 | 
 316 | ## Important notes
 317 | 
 318 | - **Follow the steps exactly as written.** Do not add extra investigation steps like importing Python modules to check docstrings, inspecting source code to verify function signatures, or running any commands not specified in the instructions. The `make coverage` step is the only verification needed — let it tell you what's wrong.
 319 | - **Never modify Python source files (`.py`).** This skill only edits `docs/source/conf.py` and doc source files (`.md`/`.rst`) in `docs/source/`. Do not add or edit docstrings, do not read Python source to check function signatures, do not inspect implementations.
 320 | - Entries are commented out in Step 3, verified in Step 6, and cleaned up in Step 8 after verification passes. Never delete uncommented entries directly.
 321 | - **Read inline comments** on entries before deciding to document them. Entries marked `# deprecated`, `# documented as ...`, `# looks unintentionally public`, or `# legacy helper` should stay in the ignore list.
 322 | - The `coverage_ignore_functions` list uses bare function names (not fully qualified), so the same name can appear multiple times for different modules. Use the module label comment above each entry to identify which module it belongs to. Be careful during Step 8 cleanup to only delete the correct commented-out lines — commented-out string entries have **quotes** (`# "func_name",`), module label comments do not.
 323 | - Always match the existing style of the target doc file — don't mix `.md` style directives into `.rst` files or vice versa.
 324 | - **Use the module label comment** (e.g., `# torch.ao.quantization.fx.convert`) as the primary guide for both the `automodule`/`currentmodule` directives and for finding the right section in the doc file.
 325 | - Always process complete module groups — never split a group across invocations.
```


---
## .claude/skills/metal-kernel/SKILL.md

```
   1 | ---
   2 | name: metal-kernel
   3 | description: Write Metal/MPS kernels for PyTorch operators. Use when adding MPS device support to operators, implementing Metal shaders, or porting CUDA kernels to Apple Silicon. Covers native_functions.yaml dispatch, host-side operators, and Metal kernel implementation.
   4 | ---
   5 | 
   6 | # Metal Kernel Writing Guide
   7 | 
   8 | This skill guides you through implementing Metal kernels for PyTorch operators on Apple Silicon.
   9 | 
  10 | **Important:** The goal of this skill is to use native Metal capabilities via the `c10/metal/` infrastructure, NOT MPSGraph. Native Metal kernels provide better control, performance, and maintainability.
  11 | 
  12 | ## Overview
  13 | 
  14 | There are two workflows covered by this skill:
  15 | 
  16 | 1. **Adding new MPS support** - Implementing a new operator from scratch
  17 | 2. **Migrating from MPSGraph** - Converting existing MPSGraph-based operators to native Metal
  18 | 
  19 | Both workflows involve:
  20 | 1. **Update dispatch** in `aten/src/ATen/native/native_functions.yaml`
  21 | 2. **Write Metal kernel** in `aten/src/ATen/native/mps/kernels/`
  22 | 3. **Implement host-side stub** in `aten/src/ATen/native/mps/operations/`
  23 | 
  24 | ## Step 1: Update native_functions.yaml
  25 | 
  26 | **Location:** `aten/src/ATen/native/native_functions.yaml`
  27 | 
  28 | ### For New Operators
  29 | 
  30 | Find the operator entry and add MPS dispatch:
  31 | 
  32 | ```yaml
  33 | # Simple MPS-specific implementation
  34 | - func: my_op(Tensor self) -> Tensor
  35 |   dispatch:
  36 |     CPU: my_op_cpu
  37 |     CUDA: my_op_cuda
  38 |     MPS: my_op_mps
  39 | 
  40 | # Shared implementation across devices (preferred for structured kernels)
  41 | - func: my_op.out(Tensor self, *, Tensor(a!) out) -> Tensor(a!)
  42 |   dispatch:
  43 |     CPU, CUDA, MPS: my_op_out
  44 | 
  45 | # Structured kernel (preferred for new ops)
  46 | - func: my_op.out(Tensor self, *, Tensor(a!) out) -> Tensor(a!)
  47 |   structured: True
  48 |   structured_inherits: TensorIteratorBase
  49 |   dispatch:
  50 |     CPU, CUDA, MPS: my_op_out
  51 | ```
  52 | 
  53 | ### For Migrating from MPSGraph
  54 | 
  55 | When migrating an existing operator from MPSGraph to native Metal, **consolidate the dispatch entry**:
  56 | 
  57 | ```yaml
  58 | # BEFORE (MPSGraph-based, separate dispatch)
  59 | - func: atan2.out(Tensor self, Tensor other, *, Tensor(a!) out) -> Tensor(a!)
  60 |   structured: True
  61 |   structured_inherits: TensorIteratorBase
  62 |   dispatch:
  63 |     CPU, CUDA: atan2_out
  64 |     MPS: atan2_out_mps  # Separate MPS implementation
  65 | 
  66 | # AFTER (native Metal, shared dispatch via stub)
  67 | - func: atan2.out(Tensor self, Tensor other, *, Tensor(a!) out) -> Tensor(a!)
  68 |   structured: True
  69 |   structured_inherits: TensorIteratorBase
  70 |   dispatch:
  71 |     CPU, CUDA, MPS: atan2_out  # MPS now uses the same stub mechanism
  72 | ```
  73 | 
  74 | **Key change:** Replace `MPS: my_op_out_mps` with adding `MPS` to the shared dispatch line (e.g., `CPU, CUDA, MPS: my_op_out`).
  75 | 
  76 | **Dispatch naming conventions:**
  77 | - `MPS: function_name_mps` - MPS-specific implementation (old MPSGraph pattern)
  78 | - `CPU, CUDA, MPS: function_name` - Shared stub implementation (native Metal pattern)
  79 | 
  80 | ## Step 2: Implement Metal Kernel
  81 | 
  82 | **Location:** `aten/src/ATen/native/mps/kernels/`
  83 | 
  84 | ### Unary Kernel Pattern
  85 | 
  86 | ```metal
  87 | // MyKernel.metal
  88 | #include <c10/metal/indexing.h>
  89 | #include <c10/metal/utils.h>
  90 | #include <metal_stdlib>
  91 | 
  92 | using namespace metal;
  93 | using namespace c10::metal;
  94 | 
  95 | // Define operation functor
  96 | struct my_op_functor {
  97 |   template <typename T>
  98 |   inline T operator()(const T x) {
  99 |     return /* your operation */;
 100 |   }
 101 | };
 102 | 
 103 | // Register for supported types
 104 | REGISTER_UNARY_OP(my_op, float, float);
 105 | REGISTER_UNARY_OP(my_op, half, half);
 106 | REGISTER_UNARY_OP(my_op, bfloat, bfloat);
 107 | ```
 108 | 
 109 | ### Binary Kernel Pattern
 110 | 
 111 | ```metal
 112 | struct my_binary_functor {
 113 |   template <typename T>
 114 |   inline T operator()(const T a, const T b) {
 115 |     return /* your operation */;
 116 |   }
 117 | };
 118 | 
 119 | REGISTER_BINARY_OP(my_binary, float, float);
 120 | REGISTER_BINARY_OP(my_binary, half, half);
 121 | ```
 122 | 
 123 | ### Binary Kernel Type Registration Macros
 124 | 
 125 | For binary operations, use the convenience macros defined in `BinaryKernel.metal`:
 126 | 
 127 | ```metal
 128 | // Floating-point types only (float, half, bfloat)
 129 | REGISTER_FLOAT_BINARY_OP(my_op);
 130 | 
 131 | // Integral types with float output (for math ops like atan2, copysign)
 132 | // Registers: long->float, int->float, short->float, uchar->float, char->float, bool->float
 133 | REGISTER_INT2FLOAT_BINARY_OP(my_op);
 134 | 
 135 | // Integral types with same-type output (for bitwise/logical ops)
 136 | // Registers: long, int, short, uchar, char, bool
 137 | REGISTER_INTEGER_BINARY_OP(my_op);
 138 | 
 139 | // Floating-point with opmath precision (for ops needing higher precision)
 140 | REGISTER_OPMATH_FLOAT_BINARY_OP(my_op);
 141 | ```
 142 | 
 143 | **Common patterns:**
 144 | - Math functions (atan2, copysign, logaddexp): Use both `REGISTER_FLOAT_BINARY_OP` and `REGISTER_INT2FLOAT_BINARY_OP`
 145 | - Comparison/logical ops (maximum, minimum): Use both `REGISTER_FLOAT_BINARY_OP` and `REGISTER_INTEGER_BINARY_OP`
 146 | - Arithmetic ops (add, sub, mul): Use both `REGISTER_FLOAT_BINARY_OP` and `REGISTER_INTEGER_BINARY_OP`
 147 | 
 148 | **Example for atan2 (supports both float and int inputs):**
 149 | ```metal
 150 | struct atan2_functor {
 151 |   template <typename T, enable_if_t<is_floating_point_v<T>, bool> = true>
 152 |   inline T operator()(const T a, const T b) {
 153 |     return static_cast<T>(precise::atan2(float(a), float(b)));
 154 |   }
 155 |   template <typename T, enable_if_t<is_integral_v<T>, bool> = true>
 156 |   inline float operator()(const T a, const T b) {
 157 |     return precise::atan2(float(a), float(b));
 158 |   }
 159 | };
 160 | 
 161 | REGISTER_FLOAT_BINARY_OP(atan2);
 162 | REGISTER_INT2FLOAT_BINARY_OP(atan2);
 163 | ```
 164 | 
 165 | ### With Scalar Parameter
 166 | 
 167 | ```metal
 168 | struct my_alpha_functor {
 169 |   template <typename T>
 170 |   inline T operator()(const T a, const T b, const T alpha) {
 171 |     return a + c10::metal::mul(alpha, b);
 172 |   }
 173 | };
 174 | 
 175 | REGISTER_UNARY_ALPHA_OP(my_alpha, float, float, float);
 176 | REGISTER_UNARY_ALPHA_OP(my_alpha, half, half, half);
 177 | ```
 178 | 
 179 | ### Type-Specialized Functor
 180 | 
 181 | ```metal
 182 | struct special_functor {
 183 |   // Floating point types
 184 |   template <typename T, enable_if_t<is_scalar_floating_point_v<T>, bool> = true>
 185 |   inline T operator()(const T x) {
 186 |     return precise::exp(x);  // Use precise math
 187 |   }
 188 | 
 189 |   // Integral types
 190 |   template <typename T, enable_if_t<is_scalar_integral_v<T>, bool> = true>
 191 |   inline float operator()(const T x) {
 192 |     return precise::exp(float(x));
 193 |   }
 194 | 
 195 |   // Complex types (float2 for cfloat, half2 for chalf)
 196 |   template <typename T, enable_if_t<is_complex_v<T>, bool> = true>
 197 |   inline T operator()(const T x) {
 198 |     // x.x = real, x.y = imaginary
 199 |     return T(/* real */, /* imag */);
 200 |   }
 201 | };
 202 | ```
 203 | 
 204 | **Note on complex types:** Complex numbers in Metal are represented as vector types:
 205 | - `c10::complex<float>` maps to `float2` (x = real, y = imaginary)
 206 | - `c10::complex<half>` maps to `half2`
 207 | 
 208 | Use `is_complex_v<T>` to specialize for complex types in functors.
 209 | 
 210 | ### Available c10/metal Utilities
 211 | 
 212 | **utils.h:**
 213 | - `opmath_t<T>` - Operation math type (half->float)
 214 | - `accum_t<T>` - Accumulation type for reductions
 215 | - `max()`, `min()` with NaN propagation
 216 | 
 217 | **special_math.h:**
 218 | - `precise::exp()`, `precise::log()`, `precise::sqrt()`
 219 | - `precise::sin()`, `precise::cos()`, `precise::tan()`
 220 | - `erf()`, `erfc()`, `erfinv()`
 221 | 
 222 | **indexing.h:**
 223 | - `REGISTER_UNARY_OP(name, in_type, out_type)`
 224 | - `REGISTER_BINARY_OP(name, in_type, out_type)`
 225 | - `REGISTER_UNARY_ALPHA_OP(name, in_type, alpha_type, out_type)`
 226 | 
 227 | ## Step 3: Implement Host-Side Stub
 228 | 
 229 | **Location:** `aten/src/ATen/native/mps/operations/`
 230 | 
 231 | Choose or create an appropriate file based on operation type:
 232 | - `UnaryKernel.mm` - Single input operations via stub dispatch
 233 | - `BinaryKernel.mm` - Two input operations via stub dispatch
 234 | - `UnaryOps.mm` / `BinaryOps.mm` - Legacy MPSGraph implementations (for reference)
 235 | - `ReduceOps.mm` - Reductions (sum, mean, max, etc.)
 236 | - Create new file for distinct operation categories
 237 | 
 238 | ### Stub Registration Pattern (Preferred for Native Metal)
 239 | 
 240 | For structured kernels that use the TensorIterator pattern:
 241 | 
 242 | ```objc
 243 | // In BinaryKernel.mm (or appropriate file)
 244 | 
 245 | static void my_op_mps_kernel(TensorIteratorBase& iter) {
 246 |   lib.exec_binary_kernel(iter, "my_op");  // "my_op" matches the functor name in .metal
 247 | }
 248 | 
 249 | // Register the MPS stub - this connects to the dispatch system
 250 | REGISTER_DISPATCH(my_op_stub, &my_op_mps_kernel)
 251 | ```
 252 | 
 253 | **For unary operations:**
 254 | ```objc
 255 | static void my_unary_mps_kernel(TensorIteratorBase& iter) {
 256 |   lib.exec_unary_kernel(iter, "my_unary");
 257 | }
 258 | 
 259 | REGISTER_DISPATCH(my_unary_stub, &my_unary_mps_kernel)
 260 | ```
 261 | 
 262 | ### Migration: Removing Old MPSGraph Implementation
 263 | 
 264 | When migrating from MPSGraph, also remove the old implementation:
 265 | 
 266 | 1. **Remove from BinaryOps.mm (or UnaryOps.mm):**
 267 |    - Delete the `TORCH_IMPL_FUNC(my_op_out_mps)` implementation
 268 |    - Remove the corresponding `#include <ATen/ops/my_op_native.h>` header
 269 | 
 270 | 2. **Add to BinaryKernel.mm (or UnaryKernel.mm):**
 271 |    - Add the static kernel function
 272 |    - Add the `REGISTER_DISPATCH` call
 273 | 
 274 | ## Step 4: Compile
 275 | 
 276 | After making changes, compile to verify everything builds correctly:
 277 | 
 278 | ```bash
 279 | cd build && ninja torch_cpu
 280 | ```
 281 | 
 282 | ## Testing
 283 | 
 284 | Basic operator support is already tested by `test_output_match` in `test/test_mps.py`. After implementing an operator, enable testing by removing expected failures:
 285 | 
 286 | ### 1. Remove from common_mps.py
 287 | 
 288 | **Location:** `torch/testing/_internal/common_mps.py`
 289 | 
 290 | Find and remove the operator from skip/xfail lists:
 291 | 
 292 | ```python
 293 | # Remove entries like:
 294 | MPS_XFAILLIST = {
 295 |     "my_op": ...,  # Remove this line
 296 | }
 297 | 
 298 | MPS_SKIPLIST = {
 299 |     "my_op": ...,  # Remove this line
 300 | }
 301 | ```
 302 | 
 303 | ### 2. Remove from OpInfo decorators
 304 | 
 305 | **Location:** `torch/testing/_internal/common_methods_invocations.py` (or related files)
 306 | 
 307 | Remove MPS-specific decorators from the OpInfo:
 308 | 
 309 | ```python
 310 | OpInfo(
 311 |     "my_op",
 312 |     # Remove decorators like:
 313 |     # decorators=[skipMPS, expectedFailureMPS("reason")],
 314 |     ...
 315 | )
 316 | ```
 317 | 
 318 | ### 3. Run tests to verify
 319 | 
 320 | ```bash
 321 | # Run the specific operator test
 322 | python test/test_mps.py -k test_output_match_my_op
 323 | 
 324 | # Or run full MPS test suite
 325 | python test/test_mps.py
 326 | ```
 327 | 
 328 | ## Checklist
 329 | 
 330 | - [ ] Added MPS dispatch to `native_functions.yaml`
 331 | - [ ] Implemented Metal kernel in `kernels/`
 332 | - [ ] Implemented host-side operator in `operations/`
 333 | - [ ] Handles empty tensors
 334 | - [ ] Handles non-contiguous tensors
 335 | - [ ] Supports required dtypes (float32, float16, bfloat16, and often complex types via float2/half2)
 336 | - [ ] Removed expected failures from `torch/testing/_internal/common_mps.py`
 337 | - [ ] Removed skip/xfail decorators from OpInfo (if applicable)
```


---
## .claude/skills/pr-review/SKILL.md

```
   1 | ---
   2 | name: pr-review
   3 | description: Review PyTorch pull requests for code quality, test coverage, security, and backward compatibility. Use when reviewing PRs, when asked to review code changes, or when the user mentions "review PR", "code review", or "check this PR".
   4 | ---
   5 | 
   6 | # PyTorch PR Review Skill
   7 | 
   8 | Review PyTorch pull requests focusing on what CI cannot check: code quality, test coverage adequacy, security vulnerabilities, and backward compatibility. Linting, formatting, type checking, and import ordering are handled by CI.
   9 | 
  10 | ## Usage Modes
  11 | 
  12 | ### No Argument
  13 | 
  14 | If the user invokes `/pr-review` with no arguments, **do not perform a review**. Instead, ask the user what they would like to review:
  15 | 
  16 | > What would you like me to review?
  17 | > - A PR number or URL (e.g., `/pr-review 12345`)
  18 | > - A local branch (e.g., `/pr-review branch`)
  19 | 
  20 | ### Local CLI Mode
  21 | 
  22 | The user provides a PR number or URL:
  23 | 
  24 | ```
  25 | /pr-review 12345
  26 | /pr-review https://github.com/pytorch/pytorch/pull/12345
  27 | ```
  28 | 
  29 | For a detailed review with line-by-line specific comments:
  30 | 
  31 | ```
  32 | /pr-review 12345 detailed
  33 | ```
  34 | 
  35 | Use `gh` CLI to fetch PR data:
  36 | 
  37 | ```bash
  38 | # Get PR details
  39 | gh pr view <PR_NUMBER> --json title,body,author,baseRefName,headRefName,files,additions,deletions,commits
  40 | 
  41 | # Get the diff
  42 | gh pr diff <PR_NUMBER>
  43 | 
  44 | # Get PR comments
  45 | gh pr view <PR_NUMBER> --json comments,reviews
  46 | ```
  47 | 
  48 | ### Local Branch Mode
  49 | 
  50 | Review changes in the current branch that are not in `main`:
  51 | 
  52 | ```
  53 | /pr-review branch
  54 | /pr-review branch detailed
  55 | ```
  56 | 
  57 | Use git commands to get branch changes:
  58 | 
  59 | ```bash
  60 | # Get current branch name
  61 | git branch --show-current
  62 | 
  63 | # Get list of changed files compared to main
  64 | git diff --name-only main...HEAD
  65 | 
  66 | # Get full diff compared to main
  67 | git diff main...HEAD
  68 | 
  69 | # Get commit log for the branch
  70 | git log main..HEAD --oneline
  71 | 
  72 | # Get diff stats (files changed, insertions, deletions)
  73 | git diff --stat main...HEAD
  74 | ```
  75 | 
  76 | For local branch reviews:
  77 | - The "Summary" should describe what the branch changes accomplish based on commit messages and diff
  78 | - Use the current branch name in the review header instead of a PR number
  79 | - All other review criteria apply the same as PR reviews
  80 | 
  81 | ### GitHub Actions Mode
  82 | 
  83 | When invoked via `@claude /pr-review` on a GitHub PR, the action pre-fetches PR
  84 | metadata and injects it into the prompt. Detect this mode by the presence of
  85 | `<formatted_context>`, `<pr_or_issue_body>`, and `<comments>` tags in the prompt.
  86 | 
  87 | The prompt already contains:
  88 | - PR metadata (title, author, branch names, additions/deletions, file count)
  89 | - PR body/description
  90 | - All comments and review comments (with file/line references)
  91 | - List of changed files with paths and change types
  92 | 
  93 | Use git commands to get the diff and commit history. The base branch name is in the
  94 | prompt context (look for `PR Branch: <head> -> <base>` or the `baseBranch` field).
  95 | 
  96 | ```bash
  97 | # Get the full diff against the base branch
  98 | git diff origin/<baseBranch>...HEAD
  99 | 
 100 | # Get diff stats
 101 | git diff --stat origin/<baseBranch>...HEAD
 102 | 
 103 | # Get commit history for this PR
 104 | git log origin/<baseBranch>..HEAD --oneline
 105 | 
 106 | # If the base branch ref is not available, fetch it first
 107 | git fetch origin <baseBranch> --depth=1
 108 | ```
 109 | 
 110 | Do NOT use `gh` CLI commands in this mode -- only git commands are available.
 111 | All PR metadata, comments, and reviews are already in the prompt context;
 112 | only the diff and commit log need to be fetched via git.
 113 | 
 114 | ## Review Philosophy
 115 | 
 116 | A single line of code can have deep cross-cutting implications: a missing device guard causes silent data corruption on multi-GPU, a missing `Composite` dispatch key breaks every out-of-tree backend, a manual dtype check instead of `TensorIterator` silently skips type promotion. **Treat every line as potentially load-bearing.**
 117 | 
 118 | Do not skim. Do not summarize the diff and move on. Read every changed line and ask: *does this interact with existing PyTorch infrastructure that the author may not know about?* When uncertain, **investigate** — spawn a sub-agent to read the surrounding code, the infrastructure the PR should be using, or the tests that should exist. The cost of a false negative (missing a real issue) is much higher than the cost of investigation.
 119 | 
 120 | ## Review Workflow
 121 | 
 122 | ### Step 1: Fetch PR Information
 123 | 
 124 | **Local CLI mode**: Use `gh` commands to get PR metadata, changed files, full diff,
 125 | existing comments/reviews, and associated issue information.
 126 | 
 127 | **Local Branch mode**: Use `git diff` and `git log` against `main` as shown in the
 128 | Local Branch Mode section above.
 129 | 
 130 | **GitHub Actions mode**: PR metadata, comments, and reviews are already in the prompt.
 131 | Use `git diff origin/<baseBranch>...HEAD` for the full diff and
 132 | `git log origin/<baseBranch>..HEAD --oneline` for the commit log.
 133 | 
 134 | ### Step 2: Understand Context
 135 | 
 136 | Before reviewing, build understanding of what the PR touches and why:
 137 | 1. Identify the purpose of the change from title/description/issue
 138 | 2. Group changes by type (new code, tests, config, docs)
 139 | 3. Note the scope of changes (files affected, lines changed)
 140 | 4. **Spawn sub-agents to read the unchanged code surrounding each changed file.** The diff alone is not enough — you need to understand the existing patterns, base classes, and infrastructure in the files being modified. For each significantly changed file, a sub-agent should read the full file (or the relevant class/function) and report back: what patterns does this file follow? What infrastructure does it use? What invariants does it maintain?
 141 | 
 142 | ### Step 3: Deep Review — Line-by-Line with Investigation
 143 | 
 144 | This is the core of the review. Go through **every changed line** in the diff and evaluate it against the review checklist in [review-checklist.md](review-checklist.md).
 145 | 
 146 | **How to use sub-agents during review:**
 147 | 
 148 | The checklist is large. You cannot hold the full context of every infrastructure system in your head. Instead, when you encounter a changed line that touches a checklist area, **spawn a sub-agent** to investigate whether the checklist item applies. For example:
 149 | 
 150 | - A PR adds a new C++ kernel → spawn a sub-agent to check: Does it use TensorIterator? DispatchStub? Structured kernels? AT_DISPATCH? Does it have a meta implementation? A Composite fallback?
 151 | - A PR adds a new test → spawn a sub-agent to check: Does an OpInfo exist for this op? Is the test device-generic? Does it use make_tensor, @dtypes, TestCase?
 152 | - A PR modifies autograd code → spawn a sub-agent to check: Is derivatives.yaml the right place? Does it use setup_context? Does it have gradcheck tests?
 153 | - A PR adds a new operator → spawn a sub-agent to check: Is it in native_functions.yaml? Does it have proper tags? A Composite dispatch? Meta/fake impls? Schema annotations?
 154 | 
 155 | **Spawn sub-agents in parallel** for independent investigation areas. A typical review of a medium PR should spawn 3-8 sub-agents. Large PRs touching multiple subsystems may need more.
 156 | 
 157 | **Checklist areas** (see [review-checklist.md](review-checklist.md) for full details):
 158 | - Code quality and design
 159 | - PyTorch infrastructure — C++ kernels (TensorIterator, DispatchStub, AT_DISPATCH, device guards), CUDA/device management, operator registration and codegen (native_functions.yaml, Composite dispatch, meta/fake implementations), autograd (derivatives.yaml, autograd.Function, gradcheck), Python utilities (pytree, __torch_function__, logging), nn module patterns, Dynamo/Inductor/compile, FX/export, type promotion, serialization, distributed, tensor subclasses
 160 | - Testing adequacy (OpInfo, ModuleInfo, device-generic tests, @dtypes, @parametrize, make_tensor)
 161 | - Security considerations
 162 | - Thread safety and concurrency (Python, C++, CPython C API, NoGIL)
 163 | - Performance implications
 164 | - Any behavior change not expected by author
 165 | 
 166 | ### Step 4: Check Backward Compatibility
 167 | 
 168 | Evaluate BC implications. See [bc-guidelines.md](bc-guidelines.md) for:
 169 | - What constitutes a BC-breaking change
 170 | - Required deprecation patterns
 171 | - Common BC pitfalls
 172 | 
 173 | For non-trivial BC questions (e.g., "does changing this default break downstream users?"), spawn a sub-agent to search for existing callers of the modified API.
 174 | 
 175 | ### Step 5: Formulate Review
 176 | 
 177 | Structure your review with actionable feedback organized by category. Every finding should be traceable to a specific line in the diff and a specific checklist item.
 178 | 
 179 | ## Review Areas
 180 | 
 181 | | Area | Focus | Reference |
 182 | |------|-------|-----------|
 183 | | Code Quality | Abstractions, patterns, complexity | [review-checklist.md](review-checklist.md) |
 184 | | API Design | New patterns, flag-based access, broader implications | [review-checklist.md](review-checklist.md) |
 185 | | C++ Kernels | TensorIterator, DispatchStub, AT_DISPATCH, structured kernels, device guards, memory format | [review-checklist.md](review-checklist.md) |
 186 | | CUDA/Device | C10_CUDA_CHECK, stream/event guards, recordStream, CUDA graphs, AcceleratorHooks | [review-checklist.md](review-checklist.md) |
 187 | | Op Registration | native_functions.yaml, Composite fallback, meta/fake impls, tags, schema annotations | [review-checklist.md](review-checklist.md) |
 188 | | Autograd | derivatives.yaml, autograd.Function patterns, gradcheck, forward-mode AD, vmap | [review-checklist.md](review-checklist.md) |
 189 | | Python Utils | __torch_function__, pytree, logging, deprecation, backends context | [review-checklist.md](review-checklist.md) |
 190 | | nn Modules | ModuleList/Dict, nn.init, parametrize, state_dict versioning, LazyModule | [review-checklist.md](review-checklist.md) |
 191 | | Dynamo/Inductor | @register_lowering, decompositions, CustomGraphPass, config.patch, graph breaks | [review-checklist.md](review-checklist.md) |
 192 | | FX/Export | PassBase, PassManager, Interpreter, subgraph rewriter, ShapeProp, make_fx | [review-checklist.md](review-checklist.md) |
 193 | | Type Promotion | elementwise_dtypes, TensorIterator dtype handling, result_type, promoteTypes | [review-checklist.md](review-checklist.md) |
 194 | | Serialization | weights_only, safe_globals, skip_data | [review-checklist.md](review-checklist.md) |
 195 | | Distributed | DeviceMesh, distributed testing with MultiThreadedPG | [review-checklist.md](review-checklist.md) |
 196 | | Tensor Subclasses | _make_wrapper_subclass, __tensor_flatten__/__unflatten__ | [review-checklist.md](review-checklist.md) |
 197 | | Testing | OpInfo, ModuleInfo, device-generic, @dtypes, @parametrize, make_tensor | [review-checklist.md](review-checklist.md) |
 198 | | Security | Injection, credentials, input handling | [review-checklist.md](review-checklist.md) |
 199 | | Performance | Regressions, device handling, memory, profiling, benchmarking | [review-checklist.md](review-checklist.md) |
 200 | | Thread Safety | Data races, GIL assumptions, NoGIL, CPython C API | [review-checklist.md](review-checklist.md) |
 201 | | BC | Breaking changes, deprecation | [bc-guidelines.md](bc-guidelines.md) |
 202 | 
 203 | ## Output Format
 204 | 
 205 | Structure your review as follows. **Omit sections where you have no findings** — don't write "No concerns" for every empty section. Only include sections with actual observations.
 206 | 
 207 | ```markdown
 208 | ## PR Review: #<number>
 209 | <!-- Or for local branch reviews: -->
 210 | ## Branch Review: <branch-name> (vs main)
 211 | 
 212 | ### Summary
 213 | Brief overall assessment of the changes (1-2 sentences).
 214 | 
 215 | ### Code Quality
 216 | [Issues and suggestions]
 217 | 
 218 | ### Infrastructure
 219 | [Flag any checklist items from the PyTorch Infrastructure section that apply.
 220 | Reference the specific infrastructure the PR should be using.]
 221 | 
 222 | ### Testing
 223 | [Testing adequacy findings — missing OpInfo usage, non-device-generic tests, etc.]
 224 | 
 225 | ### API Design
 226 | [Flag new patterns, internal-access flags, or broader implications if any.]
 227 | 
 228 | ### Security
 229 | [Issues if any]
 230 | 
 231 | ### Thread Safety
 232 | [Threading concerns if any]
 233 | 
 234 | ### Backward Compatibility
 235 | [BC concerns if any]
 236 | 
 237 | ### Performance
 238 | [Performance concerns if any]
 239 | 
 240 | ### Recommendation
 241 | **Approve** / **Request Changes** / **Needs Discussion**
 242 | 
 243 | [Brief justification for recommendation]
 244 | ```
 245 | 
 246 | ### Specific Comments (Detailed Review Only)
 247 | 
 248 | **Only include this section if the user requests a "detailed" or "in depth" review.**
 249 | 
 250 | **Do not repeat observations already made in other sections.** This section is for additional file-specific feedback that doesn't fit into the categorized sections above.
 251 | 
 252 | When requested, add file-specific feedback with line references:
 253 | 
 254 | ```markdown
 255 | ### Specific Comments
 256 | - `src/module.py:42` - Consider extracting this logic into a named function for clarity
 257 | - `test/test_feature.py:100-105` - Missing test for error case when input is None
 258 | - `torch/nn/modules/linear.py:78` - This allocation could be moved outside the loop
 259 | ```
 260 | 
 261 | ## Key Principles
 262 | 
 263 | 1. **Investigate, don't guess** - When uncertain whether a checklist item applies, spawn a sub-agent to read the relevant infrastructure code. A reviewer who guesses wrong provides negative value. A reviewer who investigates and reports findings provides immense value.
 264 | 2. **Every line matters** - A single missing `C10_CUDA_KERNEL_LAUNCH_CHECK()`, a single `weights_only=False`, a single missing Composite dispatch key — each of these is a real bug that affects real users. Do not skip lines.
 265 | 3. **No repetition** - Each observation appears in exactly one section. Never repeat the same issue, concern, or suggestion across multiple sections. If an issue spans categories (e.g., a security issue that also affects performance), place it in the most relevant section only.
 266 | 4. **Focus on what CI cannot check** - Don't comment on formatting, linting, or type errors
 267 | 5. **Be specific** - Reference file paths and line numbers. Every finding should point to a concrete line in the diff.
 268 | 6. **Be actionable** - Provide concrete suggestions with the right infrastructure to use, not vague concerns. If flagging a missing pattern, name the function/class/file the author should use.
 269 | 7. **Be proportionate** - Minor issues shouldn't block, but note them
 270 | 8. **Assume competence** - The author knows PyTorch; explain only non-obvious context. The value of this review is in catching infrastructure patterns the author may not know about, not in explaining basic programming.
 271 | 
 272 | ## Files to Reference
 273 | 
 274 | When reviewing, consult these project files for context. **Spawn sub-agents to read these** rather than relying on memory — the files change frequently:
 275 | - `CLAUDE.md` - Coding style philosophy and testing patterns
 276 | - `CONTRIBUTING.md` - PR requirements and review process
 277 | - `torch/testing/_internal/common_utils.py` - Test patterns and utilities
 278 | - `torch/testing/_internal/opinfo/core.py` - OpInfo test framework
 279 | - `aten/src/ATen/native/native_functions.yaml` - Operator declarations (for checking tags, dispatch keys, structured kernels)
 280 | - `tools/autograd/derivatives.yaml` - Backward formulas (for checking if an op should register here)
 281 | - `aten/src/ATen/native/tags.yaml` - Operator semantic tags
```


---
## .claude/skills/pr-review/bc-guidelines.md

```
   1 | # Backward Compatibility Guidelines
   2 | 
   3 | This document covers backward compatibility (BC) considerations for PyTorch PR reviews.
   4 | 
   5 | As a top level principle, ANYTHING that changes ANY user-visible behavior is potentially BC-breaking.
   6 | It will then need to be classified as a behavior not exercised in practice, a bug fix or a voluntary BC-breaking change.
   7 | 
   8 | As a reviewer, you MUST be paranoid about any potentially BC-breaking change. Indeed, one of your key role is to identify such user-visible change in behavior and ensure that the PR author worked through the implication for all of them.
   9 | 
  10 | ## What Constitutes a BC-Breaking Change
  11 | 
  12 | ### API Changes
  13 | 
  14 | | Change Type | BC Impact | Action Required |
  15 | |-------------|-----------|-----------------|
  16 | | Removing a public function/class | Breaking | Deprecation period required |
  17 | | Renaming a public API | Breaking | Deprecation period required |
  18 | | Changing function signature (removing/reordering args) | Breaking | Deprecation period required |
  19 | | Adding required arguments without defaults | Breaking | Add default value instead |
  20 | | Changing argument defaults | Potentially breaking | Document in release notes |
  21 | | Changing return type | Breaking | Deprecation period required |
  22 | | Removing, renaming or updating private API | Potentially Breaking | Validate no usage outside of PyTorch Core via global github search |
  23 | 
  24 | ### Behavioral Changes
  25 | 
  26 | | Change Type | BC Impact | Action Required |
  27 | |-------------|-----------|-----------------|
  28 | | Any user-visible behavior change | Potentially breaking | Flag to author for further discussion |
  29 | | Raising new exceptions | Potentially breaking | Validate it is expected and document |
  30 | | Changing exception types | Potentially breaking | Document in release notes |
  31 | | Changing default device | Breaking | Explicit migration |
  32 | 
  33 | ### What Is a Public API
  34 | 
  35 | Per the [official PyTorch Public API definition](https://github.com/pytorch/pytorch/wiki/Public-API-definition-and-documentation):
  36 | 
  37 | An API is **public** if:
  38 | - It's name does not start with an `_`
  39 | - Its submodule as reported by `__module__` starts with `"torch."`
  40 | - Its submodule where no name in the path starts with underscore
  41 | 
  42 | **Key rule**: If a function "looks public" and is documented on pytorch.org/docs, it is public. Undocumented functions that appear public may be changed or removed without deprecation.
  43 | 
  44 | ## Python Version Support
  45 | 
  46 | PyTorch supports all non-EOL CPython versions which means the last 5 versions.
  47 | Right now it support 3.10-3.14.
  48 | Which means that all the code must be compatible with 3.10.
  49 | 
  50 | PyTorch also supports free threaded CPython, so any C++ code must be compatible with it.
  51 | 
  52 | ## When BC Breaks Are Acceptable
  53 | 
  54 | ### With Proper Deprecation
  55 | 
  56 | BC-breaking changes are acceptable when:
  57 | 
  58 | 1. **Deprecation warning added** - At least one release with deprecation warning
  59 | 2. **Migration path documented** - Users know how to update their code
  60 | 3. **Release notes updated** - Change is clearly documented
  61 | 4. **Justified benefit** - The breaking change provides significant improvement
  62 | 
  63 | ### Deprecation Pattern
  64 | 
  65 | ```python
  66 | import warnings
  67 | 
  68 | def old_function(x, old_arg=None, new_arg=None):
  69 |     if old_arg is not None:
  70 |         warnings.warn(
  71 |             "old_arg is deprecated and will be removed in a future release. "
  72 |             "Use new_arg instead.",
  73 |             FutureWarning,
  74 |             stacklevel=2,
  75 |         )
  76 |         new_arg = old_arg
  77 |     # ... rest of implementation
  78 | ```
  79 | 
  80 | ### Without Deprecation (Rare)
  81 | 
  82 | Immediate BC breaks may be acceptable for:
  83 | 
  84 | - Security vulnerabilities
  85 | - Serious bugs that make the API unusable
  86 | - APIs explicitly marked experimental/beta
  87 | 
  88 | ## Common BC Pitfalls
  89 | 
  90 | ### 1. Changing Function Signatures
  91 | 
  92 | **Bad:**
  93 | ```python
  94 | # Before
  95 | def forward(self, x, y):
  96 |     ...
  97 | 
  98 | # After - breaks callers using positional args
  99 | def forward(self, x, z, y):
 100 |     ...
 101 | ```
 102 | 
 103 | **Good:**
 104 | ```python
 105 | # After - add new args at end with defaults
 106 | def forward(self, x, y, z=None):
 107 |     ...
 108 | ```
 109 | 
 110 | ### 2. Removing Public Attributes
 111 | 
 112 | **Bad:**
 113 | ```python
 114 | # Removing an attribute users might access
 115 | class Module:
 116 |     # self.weight removed
 117 |     pass
 118 | ```
 119 | 
 120 | **Good:**
 121 | ```python
 122 | class Module:
 123 |     @property
 124 |     def weight(self):
 125 |         warnings.warn("weight is deprecated", FutureWarning)
 126 |         return self._new_weight_implementation
 127 | ```
 128 | 
 129 | ### 3. Changing Default Behavior
 130 | 
 131 | **Bad:**
 132 | ```python
 133 | # Silently changing default from False to True
 134 | def function(x, normalize=True):  # Was normalize=False
 135 |     ...
 136 | ```
 137 | 
 138 | **Good:**
 139 | ```python
 140 | def function(x, normalize=None):
 141 |     if normalize is None:
 142 |         warnings.warn(
 143 |             "normalize default is changing from False to True in v2.5",
 144 |             FutureWarning,
 145 |         )
 146 |         normalize = False  # Keep old default during deprecation
 147 |     ...
 148 | ```
 149 | 
 150 | ### 4. Changing Exception Types
 151 | 
 152 | **Bad:**
 153 | ```python
 154 | # Users catching ValueError will miss the new exception
 155 | raise TypeError("...")  # Was ValueError
 156 | ```
 157 | 
 158 | **Good:**
 159 | ```python
 160 | # Create exception hierarchy or keep compatible
 161 | class NewError(ValueError):  # Inherits from old type
 162 |     pass
 163 | raise NewError("...")
 164 | ```
 165 | 
 166 | ## Review Checklist for BC
 167 | 
 168 | When reviewing a PR, check:
 169 | 
 170 | - [ ] **No removed public APIs** - Or proper deprecation path exists
 171 | - [ ] **No changed signatures** - Or new args have defaults
 172 | - [ ] **No changed defaults** - Or deprecation warning added
 173 | - [ ] **No changed return types/shapes** - Or migration path documented
 174 | - [ ] **No changed exception types** - Or new types inherit from old
 175 | - [ ] **Deprecation uses FutureWarning** - Not DeprecationWarning (for user-facing APIs)
 176 | - [ ] **Deprecation has stacklevel=2** - Points to user code, not library internals
 177 | - [ ] **Any other user-visible behavior change** - Give full list to author
 178 | 
 179 | ## Questions to Ask
 180 | 
 181 | When unsure about BC impact:
 182 | 
 183 | 1. Would existing user code break silently (worst case)?
 184 | 2. Would existing user code raise an exception (recoverable)?
 185 | 3. Is there a migration path that doesn't require users to change code immediately?
 186 | 4. Is this change documented in release notes?
 187 | 5. If still unsure, raise it in the review as a point to investigate further
```


---
## .claude/skills/pr-review/review-checklist.md

```
   1 | # PR Review Checklist
   2 | 
   3 | This checklist covers areas that CI cannot check. Skip items related to linting, formatting, type checking, and import ordering.
   4 | 
   5 | ## Code Quality
   6 | 
   7 | ### Abstractions and Design
   8 | 
   9 | - [ ] **Clear abstractions** - State management is explicit; no dynamic attribute setting/getting
  10 | - [ ] **Match existing patterns** - Code follows architectural patterns already in the codebase
  11 | - [ ] **No over-engineering** - Only requested changes are made; no speculative features
  12 | - [ ] **No premature abstraction** - Helpers and utilities are only created when reused; three similar lines is better than a one-use helper
  13 | - [ ] **No trivial helpers** - Avoid 1-2 LOC helper functions used only once (unless significantly improves readability)
  14 | 
  15 | ### API Design
  16 | 
  17 | When a PR introduces new API patterns, carefully evaluate the broader implications:
  18 | 
  19 | - [ ] **No flag-based internal access** - Reject patterns like `_internal=True` kwargs that gate internal functionality. These are confusing to reason about, impossible to document properly, and create BC headaches. Use a separate private function instead (e.g., `_my_internal_op()`)
  20 | - [ ] **Pattern already exists?** - Before accepting a new pattern, search the codebase to check if this pattern is already established. If not, the PR is introducing a new convention that needs stronger justification
  21 | - [ ] **Documentation implications** - Can this API be clearly documented? Flag-based access creates ambiguity about what is public vs private
  22 | - [ ] **BC implications going forward** - Will this pattern create future BC constraints?
  23 | - [ ] **Testing implications** - Does this pattern require awkward test patterns? Internal-only flags often lead to tests that use "forbidden" parameters
  24 | - [ ] **UX implications** - Is this pattern discoverable and understandable to users? Will it appear in autocomplete, type hints, or docs in confusing ways?
  25 | 
  26 | ### Code Clarity
  27 | 
  28 | - [ ] **Self-explanatory code** - Variable and function names convey intent; minimal comments needed
  29 | - [ ] **Useful comments only** - Comments explain non-obvious context that cannot be inferred locally. For large comment use the `# Note [Good note title]` and `See Note [Good note title]` to write larger comments that can be referenced from multiple places in the codebase.
  30 | - [ ] **No backward-compatibility hacks** - Unused code is deleted completely, not renamed with underscores or marked with "removed" comments
  31 | - [ ] **Appropriate complexity** - Solutions are as simple as possible for the current requirements
  32 | - [ ] **Documentation shows correct patterns only** - Docs and markdown files should show the right way to do things directly, not anti-patterns followed by corrections. Code examples must have correct indentation, names, and syntax
  33 | 
  34 | ### Initialization and Module Design
  35 | 
  36 | - [ ] **No fragile init ordering** - If multiple imports/calls must happen in a specific undocumented order, flag the design. Dependencies should be explicit or combined into a single entry point
  37 | - [ ] **Idempotent global state** - Registries and global lists that accumulate entries must handle multiple calls safely (no duplicate registration, clear cleanup story)
  38 | 
  39 | ### Common Issues to Flag
  40 | 
  41 | - Dynamic `setattr`/`getattr` for state management (prefer explicit class members)
  42 | - Unused imports, variables, or dead code paths
  43 | - Copy-pasted code that could be a shared helper
  44 | - Magic numbers without explanation
  45 | - Overly defensive error handling for impossible cases
  46 | 
  47 | ## PyTorch Infrastructure
  48 | 
  49 | When a PR touches code in the scope of any item below, **stop and investigate** whether the established infrastructure should be used. Spawn a sub-agent to read the relevant infrastructure code and determine if the PR should be using it instead of rolling its own solution.
  50 | 
  51 | ### C++ Kernel Infrastructure
  52 | 
  53 | - [ ] **TensorIterator** — PR adds or modifies C++ kernel code that iterates over tensor data (raw pointers, `at::parallel_for`, manual contiguity checks, manual output reshape/resize)
  54 | - [ ] **DispatchStub** — PR adds C++ kernel code with manual `if (device_type == kCPU) ... else if (device_type == kCUDA)` dispatch instead of using `DECLARE_DISPATCH` / `DEFINE_DISPATCH` / `REGISTER_DISPATCH` from `aten/src/ATen/native/DispatchStub.h`
  55 | - [ ] **Structured Kernels** — PR adds a new ATen operator with separate hand-written functional, inplace, and out= variants instead of using `structured: True` + `structured_delegate` in `native_functions.yaml` to generate boilerplate
  56 | - [ ] **TORCH_CHECK variants** — PR uses generic `TORCH_CHECK` for conditions that have a more specific variant: `ValueError` → `TORCH_CHECK_VALUE`, `IndexError` → `TORCH_CHECK_INDEX`, `TypeError` → `TORCH_CHECK_TYPE`, `NotImplementedError` → `TORCH_CHECK_NOT_IMPLEMENTED`
  57 | - [ ] **AT_DISPATCH macros** — PR manually switches on `dtype` with `if (dtype == kFloat) ... else if (dtype == kDouble)` instead of using `AT_DISPATCH_FLOATING_TYPES`, `AT_DISPATCH_ALL_TYPES_AND`, or the `AT_DISPATCH_SWITCH` / `AT_DISPATCH_CASE` pattern from `aten/src/ATen/Dispatch.h`
  58 | - [ ] **Device guards (RAII)** — PR manually saves/restores device context (`cudaSetDevice` + try/catch) instead of using `DeviceGuard` or `OptionalDeviceGuard` from `c10/core/DeviceGuard.h`
  59 | - [ ] **Memory format propagation** — PR allocates output tensors with `at::empty(shape, options)` (defaulting to contiguous) without calling `input.suggest_memory_format()` to preserve ChannelsLast or other input formats
  60 | - [ ] **TORCH_LIBRARY operator registration** — PR registers operators using manual dispatcher calls instead of `TORCH_LIBRARY` / `TORCH_LIBRARY_IMPL` macros from `torch/library.h`
  61 | - [ ] **TORCH_WARN_DEPRECATION** — PR uses `TORCH_WARN` for deprecation notices instead of `TORCH_WARN_DEPRECATION` which issues a proper `DeprecationWarning`
  62 | 
  63 | ### CUDA & Device Management
  64 | 
  65 | - [ ] **C10_CUDA_CHECK** — PR calls raw CUDA APIs (`cudaMalloc`, `cudaMemcpy`, etc.) without wrapping in `C10_CUDA_CHECK()` from `c10/cuda/CUDAException.h`
  66 | - [ ] **C10_CUDA_KERNEL_LAUNCH_CHECK** — PR launches CUDA kernels with `<<<>>>` syntax but doesn't follow with `C10_CUDA_KERNEL_LAUNCH_CHECK()` immediately after to detect launch errors early
  67 | - [ ] **CUDAStreamGuard** — PR manually manages CUDA streams (`cudaStreamCreate`/`cudaStreamDestroy`) instead of using `CUDAStreamGuard` or getting streams from `at::cuda::getCurrentCUDAStream()` / `getStreamFromPool()`
  68 | - [ ] **CUDAEvent synchronization** — PR uses `cudaDeviceSynchronize()` or `cudaStreamSynchronize()` for cross-stream ordering instead of `CUDAEvent::record()` + `CUDAEvent::block()` which avoids unnecessary full synchronization
  69 | - [ ] **recordStream for allocator** — PR uses tensors on non-default CUDA streams without calling `c10::cuda::CUDACachingAllocator::recordStream()` to prevent premature memory reuse
  70 | - [ ] **CUDA graph compatibility** — PR adds host-GPU synchronization, unpinned memory transfers, or other graph-unsafe operations without checking `currentStreamCaptureStatusMayInitCtx()` to detect CUDA graph capture mode
  71 | - [ ] **AcceleratorHooksInterface** — PR adds device-specific `#ifdef USE_CUDA` blocks in generic code instead of using `AcceleratorHooksInterface` from `aten/src/ATen/detail/AcceleratorHooksInterface.h` for device-agnostic behavior
  72 | - [ ] **DeviceGuardImplInterface** — PR implements custom device management without going through `DeviceGuardImplInterface` from `c10/core/impl/DeviceGuardImplInterface.h`, bypassing the standard device abstraction layer
  73 | 
  74 | ### Operator Registration & Codegen
  75 | 
  76 | - [ ] **native_functions.yaml** — PR adds a new ATen operator by writing manual C++ bindings and Python wrappers instead of declaring it in `aten/src/ATen/native/native_functions.yaml` and letting codegen produce the boilerplate
  77 | - [ ] **Operator tags** — PR adds an operator to `native_functions.yaml` without appropriate tags from `tags.yaml` (e.g., `pointwise`, `reduction`, `view_copy`, `core`, `pt2_compliant_tag`)
  78 | - [ ] **Missing Composite fallback** — PR adds a new operator to `native_functions.yaml` with only backend-specific dispatch keys (e.g., `CPU`, `CUDA`) but no `CompositeImplicitAutograd` or `CompositeExplicitAutograd` fallback. Without a Composite entry, the op will fail on all backends that don't have an explicit registration (XLA, MPS, HPU, PrivateUse1, etc.). Every new op should either have a Composite implementation or a clear justification for why it can only work on specific backends
  79 | - [ ] **Meta function registration** — PR adds a new operator without a meta (shape-only) implementation, blocking `torch.compile` and `torch.export`. Meta implementations can be registered in Python via `@register_meta` from `torch/_meta_registrations.py`, via `torch.library.impl(..., "Meta")`, or in C++ as a structured kernel with a `meta` dispatch key or via any `Composite` dispatch key in `native_functions.yaml` (since Composite kernels automatically work on Meta tensors)
  80 | - [ ] **Fake tensor implementation** — PR adds a custom op (registered via `torch.library`) without a fake implementation. Custom ops need `@register_fake` / `my_op.register_fake()` for `torch.compile` to trace through the op. For C++ ops registered via `native_functions.yaml`, the meta kernel serves this purpose. For Python `torch.library` custom ops, use `@torch.library.register_fake("mylib::my_op")` or `@my_op.register_fake` to provide a shape/dtype-only implementation. The fake impl receives `FakeImplCtx` with `ctx.new_dynamic_size()` for data-dependent output shapes
  81 | - [ ] **Schema annotations** — PR defines operator schemas without proper alias annotations (`Tensor(a)`, `Tensor(a!)`) for view and in-place ops, which breaks functionalization and autograd's alias tracking
  82 | 
  83 | ### Autograd
  84 | 
  85 | - [ ] **derivatives.yaml** — PR writes a custom `autograd.Function` subclass for an operation that should have its backward formula registered in `tools/autograd/derivatives.yaml` (the centralized backward formula registry for ATen ops)
  86 | - [ ] **setup_context pattern** — PR writes `autograd.Function` with `forward(ctx, ...)` (legacy pattern) instead of separated `forward(...)` + `setup_context(ctx, inputs, output)` which is required for functorch compatibility (vmap, grad)
  87 | - [ ] **ctx.save_for_backward** — PR saves tensors in `autograd.Function` via `ctx.my_tensor = tensor` instead of `ctx.save_for_backward(tensor)`, causing memory leaks by keeping tensors alive longer than needed
  88 | - [ ] **gradcheck testing** — PR adds custom backward logic but doesn't test it with `torch.autograd.gradcheck()` / `gradgradcheck()` which verify numerical correctness of gradients via finite differences
  89 | - [ ] **Forward-mode AD** — PR adds a new differentiable op with backward formula in `derivatives.yaml` but doesn't add a `result:` entry for forward-mode AD (JVP). Can often use `auto_element_wise` or `auto_linear` for automatic generation
  90 | - [ ] **register_autograd for custom ops** — PR writes a full `autograd.Function` subclass for a custom op registered via `torch.library` instead of using the simpler `@my_op.register_autograd(backward, setup_context=...)` API
  91 | - [ ] **Vmap rule for custom ops** — PR adds a custom op or `autograd.Function` without a vmap rule (`generate_vmap_rule = True` or manual `vmap()` static method), breaking `torch.vmap` support
  92 | 
  93 | ### Python Utilities
  94 | 
  95 | - [ ] **__torch_function__ support** — PR adds a new Python-level function that takes tensors but doesn't check `has_torch_function()` / call `handle_torch_function()`, breaking tensor subclass dispatch
  96 | - [ ] **Pytree registration** — PR manually flattens/unflattens custom container types (dataclasses, named tuples) instead of registering them with `torch.utils._pytree.register_pytree_node()` or `register_dataclass()`
  97 | - [ ] **tree_map** — PR manually walks nested structures of tensors with recursive functions instead of using `torch.utils._pytree.tree_map()`
  98 | - [ ] **_DecoratorContextManager** — PR implements a context manager that should also work as a decorator but doesn't inherit from `torch.utils._contextlib._DecoratorContextManager`
  99 | - [ ] **Deprecation utilities** — PR deprecates a function using ad-hoc `warnings.warn()` calls instead of PyTorch's deprecation infrastructure (`lazy_deprecated_import` for module-level, `TORCH_WARN_DEPRECATION` for C++)
 100 | - [ ] **No print statements** — PR adds `print()` calls for debugging or diagnostics. Use `torch._logging` utilities instead (`getArtifactLogger`, `LazyString`, `warning_once`). For the `torch.compile` stack specifically, use `trace_structured()` for structured artifacts that integrate with `tlparse` for production debugging. No bare `print()` should ever land in production code
 101 | - [ ] **torch.backends context** — PR manually saves/restores backend flags (`cudnn.deterministic`, etc.) instead of using the `torch.backends.cudnn.flags()` context manager
 102 | 
 103 | ### nn Module Patterns
 104 | 
 105 | - [ ] **ModuleList / ModuleDict** — PR stores submodules in plain Python `list` or `dict` instead of `nn.ModuleList` or `nn.ModuleDict`, causing them to be invisible to `parameters()`, `to()`, `state_dict()`, etc.
 106 | - [ ] **nn.init methods** — PR manually initializes weights with `self.weight.data.normal_(0, 0.01)` instead of using `torch.nn.init.kaiming_uniform_()`, `xavier_uniform_()`, etc., which handle fan-in/fan-out calculations correctly
 107 | - [ ] **Parametrization framework** — PR implements custom weight reparameterization via forward pre-hooks (the deprecated pattern) instead of using `torch.nn.utils.parametrize.register_parametrization()`
 108 | - [ ] **_load_from_state_dict versioning** — PR changes a module's parameter layout without implementing `_load_from_state_dict()` for backward-compatible loading of old checkpoints (see BatchNorm's `_version = 2` pattern)
 109 | - [ ] **clip_grad_norm_** — PR manually computes gradient norms and clips in training loops instead of using `torch.nn.utils.clip_grad_norm_()` or `clip_grad_value_()`
 110 | - [ ] **LazyModule pattern** — PR implements deferred parameter initialization with manual shape inference in `forward()` instead of using `LazyModuleMixin` with `UninitializedParameter`
 111 | 
 112 | ### Dynamo / Inductor / Compile
 113 | 
 114 | - [ ] **@register_lowering** — PR adds Inductor support for an op by modifying core lowering code instead of using `@register_lowering(aten.my_op)` from `torch/_inductor/lowering.py` with automatic type promotion and broadcasting
 115 | - [ ] **Inductor decompositions** — PR writes a full Inductor lowering for a complex op that can be decomposed into simpler already-lowered ops via `@register_decomposition` in `torch/_inductor/decomposition.py`
 116 | - [ ] **CustomGraphPass** — PR writes ad-hoc FX graph iteration for Inductor optimization instead of implementing `CustomGraphPass` (with `__call__` and `uuid()`) from `torch/_inductor/custom_graph_pass.py`
 117 | - [ ] **config.patch** — PR manually saves/restores Dynamo or Inductor config values in tests instead of using `torch._dynamo.config.patch()` as a decorator or context manager
 118 | - [ ] **Graph break hints** — PR calls `unimplemented()` in Dynamo without providing `gb_type`, `explanation`, or `hints` (like `SUPPORTABLE`, `FUNDAMENTAL`), making it hard for users to understand and fix graph breaks
 119 | - [ ] **Dynamo trace rules** — PR adds manual skip/inline logic in Dynamo variable tracking instead of updating `manual_torch_name_rule_map`, `MOD_INLINELIST`, or `MOD_SKIPLIST` in `torch/_dynamo/trace_rules.py`
 120 | - [ ] **torch.compile compatibility** — PR adds a new op or modifies an existing one without verifying it works under `torch.compile` (should test with `pt2_compliant_tag` and run opcheck)
 121 | 
 122 | ### FX / Export
 123 | 
 124 | - [ ] **FX PassBase** — PR writes a custom FX graph transformation with manual graph walking instead of inheriting from `PassBase` (with `requires()`, `call()`, `ensures()`) from `torch/fx/passes/infra/pass_base.py`
 125 | - [ ] **FX PassManager** — PR manually orders and applies multiple FX passes instead of using `PassManager` with `this_before_that_pass_constraint` from `torch/fx/passes/infra/pass_manager.py`
 126 | - [ ] **FX Interpreter** — PR manually iterates FX graph nodes and tracks values in a dict instead of subclassing `torch.fx.Interpreter` which provides structured `run_node()` / `call_function()` / `call_module()` overrides
 127 | - [ ] **Subgraph rewriter** — PR manually matches and replaces graph patterns instead of using `replace_pattern()` from `torch/fx/subgraph_rewriter.py`
 128 | - [ ] **ShapeProp** — PR manually executes FX graphs to annotate shapes on nodes instead of using `ShapeProp(gm).propagate(*args)` from `torch/fx/passes/shape_prop.py`
 129 | - [ ] **torch.export dynamic shapes** — PR hard-codes tensor shapes in export constraints instead of using `Dim(name, min, max)` and `dims()` from `torch/export/dynamic_shapes.py`
 130 | - [ ] **make_fx** — PR manually initializes `torch.fx.Tracer` for proxy-based tracing instead of using `make_fx(f, tracing_mode="symbolic")` from `torch/fx/experimental/proxy_tensor.py`
 131 | 
 132 | ### Type Promotion & Dtypes
 133 | 
 134 | - [ ] **elementwise_dtypes / TensorIterator** — PR manually implements type promotion logic for elementwise ops. In Python, use `elementwise_dtypes()` from `torch/_prims_common/` with the appropriate `ELEMENTWISE_TYPE_PROMOTION_KIND`. In C++, use `TensorIteratorConfig` which handles type promotion automatically: call `.promote_inputs_to_common_dtype(true)` and `.cast_common_dtype_to_outputs(true)` on the config builder, then `TensorIterator` computes `common_dtype()` for the kernel and handles all input/output casting. Kernels should operate on `iter.common_dtype()` via `AT_DISPATCH` rather than manually checking and promoting dtypes
 135 | - [ ] **result_type** — PR manually resolves output dtype from mixed-dtype inputs instead of using `torch.result_type()` (Python) or `at::result_type()` / `update_result_type_state()` (C++)
 136 | - [ ] **Complex dtype handling** — PR manually maps between complex and real dtypes (e.g., `complex64` to `float32`) instead of using `corresponding_real_dtype()` / `corresponding_complex_dtype()` from `torch/_prims_common/`
 137 | - [ ] **promoteTypes** — PR writes manual dtype promotion tables instead of using `c10::promoteTypes(a, b)` from `c10/core/ScalarType.h`
 138 | 
 139 | ### Serialization
 140 | 
 141 | - [ ] **weights_only=False** — PR adds `torch.load(..., weights_only=False)`, explicitly opting out of safe deserialization. `weights_only=True` is already the default; setting it to `False` enables arbitrary code execution via pickle and is almost never the right thing to do. Flag this and ask the author to register safe globals via `torch.serialization.add_safe_globals()` instead
 142 | - [ ] **safe_globals** — PR adds new types to serialization that should be loadable with `weights_only=True` but doesn't register them via `torch.serialization.add_safe_globals()`
 143 | - [ ] **skip_data context** — PR implements metadata-only checkpoint inspection by reading full tensors instead of using `torch.serialization.skip_data()` context manager
 144 | 
 145 | ### Distributed
 146 | 
 147 | - [ ] **DeviceMesh** — PR manually creates multiple `ProcessGroup`s for multi-dimensional parallelism (TP + DP) instead of using `DeviceMesh` from `torch/distributed/device_mesh.py` which manages this automatically
 148 | - [ ] **Distributed testing** — PR spawns multiple real processes for distributed unit tests instead of using `MultiThreadedPG` from `torch/testing/_internal/distributed/multi_threaded_pg.py` for single-process testing
 149 | 
 150 | ### Tensor Subclasses
 151 | 
 152 | - [ ] **_make_wrapper_subclass** — PR creates tensor subclasses by calling `torch.Tensor.__new__()` directly instead of using `torch.Tensor._make_wrapper_subclass()` which properly sets up the subclass wrapper
 153 | - [ ] **__tensor_flatten__ / __tensor_unflatten__** — PR adds a tensor subclass without implementing `__tensor_flatten__()` and `__tensor_unflatten__()`, breaking serialization and `torch.compile` support
 154 | 
 155 | ### Miscellaneous
 156 | 
 157 | - [ ] **torch._check** — PR uses `assert` or `if not cond: raise` in Python op implementations instead of `torch._check()` / `torch._check_is_size()` which work correctly with meta tensors and symbolic shapes
 158 | - [ ] **C++ extension building** — PR uses raw `setuptools` or `distutils` for building C++ extensions instead of `torch.utils.cpp_extension.CppExtension` / `CUDAExtension` / `load_inline()` which handle compiler flags, ABI, and includes
 159 | - [ ] **register_package for custom devices** — PR adds custom device serialization handling by monkey-patching `torch.save`/`torch.load` instead of using `torch.serialization.register_package()` to register location tag and restore functions
 160 | - [ ] **@register_backend** — PR adds a `torch.compile` backend by manually modifying internal dispatch tables instead of using `@torch._dynamo.backends.registry.register_backend(name=...)`
 161 | 
 162 | ## Testing
 163 | 
 164 | ### Test Existence
 165 | 
 166 | - [ ] **Tests exist** - New functionality has corresponding tests
 167 | - [ ] **Tests are in the right place** - Tests should be added to an existing test file next to other related tests
 168 | - [ ] **New test file is rare** - New test file should only be added when new major features are added
 169 | 
 170 | ### Test Patterns
 171 | 
 172 | - [ ] **Proper module ownership** - Test files must have a real `# Owner(s): ["module: ..."]` label, not `"module: unknown"`. The author should create a new module label if needed and add themselves as owner
 173 | - [ ] **Use OpInfo** - Any testing for an operator or a cross-cutting feature must be done via OpInfo. Flag manual tests (e.g., `assertEqual(a + b, expected)`) for operators that already have OpInfo entries — these are redundant and will rot. When a PR adds dtype/device support to an operator, the testing should come from existing OpInfo infrastructure automatically (e.g., by adding the dtype to the operator's OpInfo `dtypes`), not from new manual tests. Likewise, a test checking a specific behavior for a single operator should not be a standalone test — the OpInfo infrastructure for that test category should be updated to cover the behavior across all applicable operators
 174 | - [ ] **Use ModuleInfo** - Manual forward/backward tests for `nn.Module` subclasses should use `ModuleInfo` from `torch/testing/_internal/common_modules.py` and the `@modules` decorator instead of hand-written per-module tests
 175 | - [ ] **Use TestCase** - Tests inherit from `torch.testing._internal.common_utils.TestCase`
 176 | - [ ] **Use run_tests** - Test file ends with `if __name__ == "__main__": run_tests()`
 177 | - [ ] **Use assertEqual for tensors** - Tensor comparisons use `assertEqual`, not raw assertions or `torch.allclose`
 178 | - [ ] **Device generic** - Any test checking compute result should happen in a device-generic test class (taking device as an argument) via `instantiate_device_type_tests`. Device-specific tests should be very rare and in device-specific test files
 179 | - [ ] **Use @dtypes** - PR writes separate test methods per dtype or manual `for dtype in [...]` loops instead of using the `@dtypes(...)` decorator from `common_device_type.py`
 180 | - [ ] **Use @parametrize** - PR duplicates test methods that differ only in a parameter instead of using `@parametrize` from `common_utils.py`
 181 | - [ ] **Use @ops for operator tests** - PR writes manual per-operator test iterations instead of using the `@ops(op_db)` decorator which automatically parametrizes tests over OpInfo entries
 182 | - [ ] **Use make_tensor** - PR creates test tensors with `torch.rand(shape)` (implicit CPU, implicit dtype) instead of `make_tensor(shape, device=device, dtype=dtype)` from `torch.testing` which enforces explicit device/dtype
 183 | - [ ] **Use common dtype groups** - PR manually lists dtypes like `[torch.float32, torch.float64]` instead of using helpers like `floating_types()`, `all_types_and_complex()`, etc. from `common_dtype.py`
 184 | - [ ] **Use toleranceOverride** - PR hard-codes tolerance values in individual assertions instead of using `@toleranceOverride` / `@precisionOverride` decorators which set per-dtype tolerances
 185 | - [ ] **Use DecorateInfo for OpInfo skips** - PR adds `@skipIf` conditionals inside OpInfo test methods instead of using `DecorateInfo` in the OpInfo's `skips` or `decorators` tuple
 186 | - [ ] **Use largeTensorTest** - PR manually checks free memory before large-tensor tests instead of using `@largeTensorTest("4 GB")` decorator from `common_device_type.py`
 187 | - [ ] **Descriptive test names** - Test method names describe what is being tested
 188 | 
 189 | ### Test Quality
 190 | 
 191 | - [ ] **Edge cases covered** - Tests include boundary conditions, empty inputs, error cases
 192 | - [ ] **Error conditions tested** - Expected exceptions are tested with `assertRaises` or `assertRaisesRegex`
 193 | - [ ] **No duplicated test logic** - Similar tests share a private helper method (e.g., `_test_foo(config)`) called from individual tests with different configs
 194 | 
 195 | **Example of good test structure:**
 196 | ```python
 197 | def _test_feature_with_config(self, flag, expected_shape):
 198 |     """Shared test logic called by device-specific tests."""
 199 |     x = torch.randn(10)
 200 |     result = my_feature(x, flag)
 201 |     self.assertEqual(result.shape, expected_shape)
 202 | 
 203 | def test_feature_enabled(self):
 204 |     self._test_feature_with_config(True, (10, 10))
 205 | 
 206 | def test_feature_disabled(self):
 207 |     self._test_feature_with_config(False, (10, 5))
 208 | ```
 209 | 
 210 | ### Common Testing Issues
 211 | 
 212 | - Tests that only check the happy path without error cases
 213 | - Duplicated test code that should be a parameterized helper
 214 | - Manual operator tests that duplicate existing OpInfo coverage — the fix should update the OpInfo's dtype list instead
 215 | - Tests that don't clean up resources (files, CUDA memory)
 216 | - Flaky tests (timing-dependent, order-dependent, golden value)
 217 | - Tests that skip without clear justification
 218 | 
 219 | ## Security
 220 | 
 221 | ### CI/CD and Workflow Security
 222 | 
 223 | When reviewing changes to workflows, build scripts, or CI configuration:
 224 | 
 225 | - [ ] **No secrets in workflow files** - PyTorch does not use repo secrets mechanism due to non-ephemeral runners; secrets can be compromised via reverse shell attacks
 226 | - [ ] **Ephemeral runners for sensitive jobs** - Binary builds, uploads, and merge actions must run on ephemeral runners only
 227 | - [ ] **No cache-dependent binaries in sensitive contexts** - sccache-backed builds are susceptible to cache corruption; these artifacts should not access sensitive info or be published for general use
 228 | - [ ] **Protected branch rules respected** - Changes to merge rules, release workflows, or deployment environments require extra scrutiny
 229 | - [ ] **Immutable artifact references** - Docker images use immutable tags; no overwriting of published artifacts
 230 | 
 231 | ### PyTorch API Security
 232 | 
 233 | When reviewing changes to PyTorch APIs and user-facing code:
 234 | 
 235 | - [ ] **Model loading surfaces** - `torch.load` has a large attack surface; changes should not expand unsafe deserialization. Prefer safetensors for new serialization APIs
 236 | - [ ] **TorchScript security** - TorchScript models are executable code; introspection tools like `torch.utils.model_dump` can execute code from untrusted models and should not be used
 237 | - [ ] **Distributed primitives** - `torch.distributed`, RPC, and TCPStore have no auth/encryption and accept connections from anywhere; they are for internal networks only, not untrusted environments
 238 | - [ ] **No new pickle usage** - Avoid adding `pickle.load` or `torch.load` without `weights_only=True` on paths that could receive untrusted data
 239 | 
 240 | ## Thread Safety & Concurrency
 241 | 
 242 | ### Python Threading
 243 | 
 244 | - [ ] **No unprotected shared mutable state** - Shared data structures accessed from multiple threads are protected by locks or are inherently thread-safe
 245 | - [ ] **Lock ordering** - When multiple locks are acquired, ordering is consistent to avoid deadlocks
 246 | - [ ] **No GIL-reliant correctness** - Code that mutates shared state should not rely on the GIL for thread safety, since the GIL may not be present in free-threaded builds
 247 | 
 248 | ### C++ Threading
 249 | 
 250 | - [ ] **No data races** - Shared mutable state is protected by mutexes or uses atomics with appropriate memory ordering
 251 | - [ ] **RAII lock guards** - Prefer `std::lock_guard` or `std::unique_lock` over manual `lock()`/`unlock()` to ensure exception-safe unlocking
 252 | - [ ] **No lock-order inversions** - When acquiring multiple locks, a consistent global ordering is followed
 253 | - [ ] **Correct atomic memory ordering** - `std::memory_order_relaxed` is only used when ordering with other operations is genuinely unnecessary; default to `seq_cst` or use `acquire`/`release` pairs
 254 | 
 255 | ### CPython C API Thread Safety
 256 | 
 257 | This is particularly important for PyTorch's autograd, which has multi-threaded C++ code calling into the CPython C API.
 258 | 
 259 | - [ ] **GIL held for Python object access** - Any code that touches `PyObject*` (incref, decref, attribute access, container mutation) must hold the GIL. When releasing the GIL for long-running C++ work (`Py_BEGIN_ALLOW_THREADS`), verify no Python objects are accessed in that region
 260 | - [ ] **Borrowed references across GIL release** - Borrowed references (`PyTuple_GET_ITEM`, `PyList_GET_ITEM`) become unsafe if the GIL is released and reacquired, since another thread may have mutated the container
 261 | - [ ] **Decref-before-update hazard** - When replacing an item in a container (tuple, list, dict), update the container slot first, then `Py_DECREF` the old value. Decref can trigger `__del__` finalizers that re-enter and observe the container in an inconsistent state. Without the GIL (free-threaded builds), this is also a data race.
 262 | 
 263 | ### Free-Threaded Python (NoGIL, PEP 703)
 264 | 
 265 | CPython 3.13t+ can run without the GIL. Code that was previously safe under the GIL may have races in free-threaded builds:
 266 | 
 267 | - [ ] **No implicit GIL serialization assumptions** - Code paths that assume only one thread can execute Python at a time are broken under NoGIL. Look for shared mutable state accessed from C extensions without explicit locking
 268 | - [ ] **Raw `PyTuple_SET_ITEM` / `PyList_SET_ITEM`** - These are raw slot writes with no memory ordering guarantees. In free-threaded builds, concurrent reads from other threads may see stale or torn values. Consider whether the data structure could be accessed concurrently and whether atomic operations or the thread-safe API alternatives are needed
 269 | - [ ] **Module-level mutable state in C extensions** - Global/static `PyObject*` variables or C-level caches accessed from multiple threads need synchronization in NoGIL builds
 270 | 
 271 | ### PyTorch-Specific Concurrency
 272 | 
 273 | - [ ] **Autograd engine multi-threading** - The autograd engine runs node `apply()` methods from worker threads. Code in custom autograd node implementations must be safe for concurrent execution across different nodes, and must hold the GIL when accessing Python objects
 274 | - [ ] **CUDA stream synchronization** - Operations across different CUDA streams require explicit synchronization (`cudaStreamSynchronize`, `cudaEventRecord`/`cudaStreamWaitEvent`). Missing synchronization can cause silent data corruption
 275 | - [ ] **DataLoader worker safety** - Objects shared between the main process and DataLoader worker processes (or threads) must be fork-safe or use appropriate IPC mechanisms
 276 | 
 277 | ## Performance
 278 | 
 279 | ### Obvious Regressions
 280 | 
 281 | - [ ] **No unnecessary allocations** - Tensors are not repeatedly created in hot loops
 282 | - [ ] **Appropriate in-place operations** - Use in-place ops where possible in performance-critical paths
 283 | - [ ] **No Python loops over tensors** - Prefer vectorized operations over iterating tensor elements
 284 | 
 285 | ### Device Handling
 286 | 
 287 | - [ ] **Device consistency** - Operations don't unexpectedly move tensors between devices
 288 | - [ ] **CUDA considerations** - CUDA-specific code handles synchronization appropriately
 289 | - [ ] **MPS compatibility** - Metal Performance Shaders are considered if applicable
 290 | 
 291 | ### Memory Patterns
 292 | 
 293 | - [ ] **No memory leaks** - Temporary tensors are freed, no circular references
 294 | - [ ] **Efficient data structures** - Appropriate containers for access patterns
 295 | - [ ] **Gradient memory** - Proper use of `no_grad()`, `detach()` to avoid unnecessary graph retention
 296 | 
 297 | ### Profiling & Benchmarking
 298 | 
 299 | - [ ] **Use torch.profiler** - PR adds manual `time.time()` instrumentation instead of using `torch.profiler.profile()` context manager with `schedule()` and `tensorboard_trace_handler()`
 300 | - [ ] **Use torch.utils.benchmark.Timer** - PR benchmarks with `time.time()` loops instead of `torch.utils.benchmark.Timer` which handles warmup, statistics, and proper CUDA synchronization
 301 | 
 302 | ### Common Performance Issues
 303 | 
 304 | - Creating new tensors inside training loops instead of pre-allocating
 305 | - Synchronous CUDA operations where async would work
 306 | - Keeping computation graph alive longer than needed
 307 | - Redundant clones or copies
```


---
## .claude/skills/pt2-bug-basher/SKILL.md

```
   1 | ---
   2 | name: pt2-bug-basher
   3 | disable-model-invocation: true
   4 | description: Debug PyTorch 2 compiler stack failures including Dynamo graph breaks, Inductor codegen errors, AOTAutograd crashes, and accuracy mismatches. Use when encountering torch.compile errors, BackendCompilerFailed exceptions, recompilation issues, Triton kernel failures, FX graph problems, or when the user mentions debugging PT2, Dynamo, Inductor, or compiled model issues.
   5 | ---
   6 | 
   7 | # PT2 Bug Basher
   8 | 
   9 | Debug test failures and runtime errors in the PyTorch 2 compiler stack (Dynamo, Inductor, AOTAutograd, FX graphs).
  10 | 
  11 | ## Workflow Summary
  12 | 
  13 | 1. **Reproduce** -- Get a consistent reproduction of the failure
  14 | 2. **Minimize** -- Reduce the repro to the smallest possible standalone case. Strip away unrelated model logic, use minimal tensor shapes, and isolate the specific op or pattern that triggers the bug.
  15 | 3. **Add a unit test** -- **Do this BEFORE diving into code search or root cause investigation.** Add a failing test to the codebase that captures the bug. Place it in a specific, topic-appropriate test file (e.g., `test/dynamo/test_repros.py`, `test/inductor/test_torchinductor.py`, `test/export/test_export.py`). **Avoid `test/dynamo/test_misc.py`** — it is already oversized; find a more specific test file that matches the area of the bug. Use `torch.testing._internal.common_utils.TestCase` and `run_tests`. The test must fail before the fix and pass after. Having the test first keeps you grounded — you know exactly what "fixed" looks like before you start exploring the codebase.
  16 | 4. **Gather logs** -- Run with appropriate `TORCH_LOGS` settings
  17 | 5. **Classify** -- Use the [Error Triage](#error-triage) table to identify the category
  18 | 6. **Inspect artifacts** -- Check FX graphs, IR, and generated code via `TORCH_COMPILE_DEBUG=1`
  19 | 7. **Identify root cause** -- Trace from the error back through the compilation pipeline
  20 | 8. **Fix** -- Apply the fix
  21 | 9. **Verify** -- Run the new unit test AND nearby related existing tests (e.g., if you changed how `is_exporting` works, also run the existing `test_is_exporting` export test). Use `pytest -k` to quickly run related tests by name. The task is not complete until all pass.
  22 | 10. **Self-review** -- Use the `/pr-review` skill to review your own changes before presenting them. Fix any issues it flags.
  23 | 11. **Celebrate** -- Summarize the changes: explain the root cause, what was changed and why, and which tests were added/verified. Then tell the user the bug is squashed. Include a fun, varied motivational message or easter egg to keep spirits high (e.g., a pun, a quote, an ASCII art bug getting squashed). Keep it short and different each time.
  24 | 
  25 | ## Investigation Strategy
  26 | 
  27 | ### Prefer direct tools over meta_codesearch
  28 | 
  29 | Use `Grep`, `Glob`, and `Read` directly for code exploration. **Do not spawn `meta_codesearch` agents** — they are slow and expensive. The [Architectural Knowledge](#architectural-knowledge) and [Key Source Files](#key-source-files) sections below should give you enough context to know where to look. A targeted `Grep` for a function name is always faster.
  30 | 
  31 | ### Know which compilation mode you're in
  32 | 
  33 | Before reading implementation code, determine the compilation mode. These share code but diverge in important ways:
  34 | - **`torch.compile`** -- Dynamo + Inductor. `tx.export=False`, no `_compiling_state_context()`.
  35 | - **`torch.export` (strict)** -- `tx.export=True`, `_compiling_state_context()` active.
  36 | - **`torch.export` (non-strict, **the default**)** -- Uses Dynamo via `fullgraph_capture` but `tx.export` may differ from strict. `_compiling_state_context()` active. Check `torch._export.config.use_new_tracer_experimental` — it changes which code path is used.
  37 | 
  38 | ### Distinguish trace-time vs runtime
  39 | 
  40 | Many PT2 bugs come from confusing these two:
  41 | - **Trace-time**: Inside Dynamo's symbolic interpreter. Dynamo intercepts function calls and may constant-fold them (e.g., `is_exporting()` → `ConstantVariable(True)`).
  42 | - **Runtime**: Real tensors, real Python calls, module-level flags like `torch.compiler._is_exporting_flag`.
  43 | 
  44 | When debugging, add temporary `print()` statements directly in the source file rather than monkey-patching from outside — dispatch chains make monkey-patching unreliable.
  45 | 
  46 | ## Gathering Information
  47 | 
  48 | Pick the right diagnostic tool based on the error category:
  49 | 
  50 | - **Quick overview**: `TORCH_LOGS="+dynamo,graph_breaks,recompiles" python your_script.py`
  51 | - **Full debug artifacts**: `TORCH_COMPILE_DEBUG=1 python your_script.py` — creates `torch_compile_debug/` with FX graphs, Inductor IR, and generated code
  52 | - **Generated code only**: `TORCH_LOGS="output_code" python your_script.py`
  53 | - **Structured tracing**: `TORCH_TRACE=/path/to/trace python your_script.py` then `tlparse /path/to/trace`
  54 | - **Single-threaded (for pdb)**: `TORCHINDUCTOR_COMPILE_THREADS=1 python your_script.py`
  55 | 
  56 | ## Error Triage
  57 | 
  58 | Classify the failure using the error message and traceback:
  59 | 
  60 | | Error Pattern | Category | Jump To |
  61 | |---|---|---|
  62 | | `Unsupported: ...` or `graph break` in logs | Graph break | [Graph Breaks](#graph-breaks) |
  63 | | `BackendCompilerFailed` | Inductor/backend crash | [Backend Failures](#backend-compiler-failures) |
  64 | | `RecompileError` or `cache_size_limit` | Recompilation | [Recompilation](#recompilation-issues) |
  65 | | Accuracy mismatch / wrong numerical output | Accuracy | [Accuracy](#accuracy-issues) |
  66 | | `InternalTorchDynamoError` | Dynamo bug | [Internal Errors](#internal-dynamo-errors) |
  67 | | Segfault or CUDA IMA | Runtime crash | [Runtime Crashes](#runtime-crashes) |
  68 | | Triton assertion / index out of bounds | Triton kernel bug | [Triton Failures](#triton-kernel-failures) |
  69 | 
  70 | ## Debugging by Category
  71 | 
  72 | ### Graph Breaks
  73 | 
  74 | Graph breaks split the compiled graph into smaller subgraphs, often causing performance regressions or unexpected behavior.
  75 | 
  76 | **Diagnosis:**
  77 | ```bash
  78 | TORCH_LOGS="graph_breaks" python your_script.py
  79 | ```
  80 | 
  81 | **Key files:**
  82 | - `torch/_dynamo/exc.py` -- `Unsupported` exception class
  83 | - `torch/_dynamo/variables/` -- where most graph break decisions happen
  84 | 
  85 | **Common causes:**
  86 | - Unsupported Python constructs (data-dependent control flow, unsupported builtins)
  87 | - Tensor operations that can't be traced (in-place ops on inputs, unsupported dtypes)
  88 | - Calls to non-traceable functions
  89 | 
  90 | **Fix approach:**
  91 | 1. Read the graph break message to identify the unsupported operation
  92 | 2. Check if there's a decomposition or supported alternative
  93 | 3. If the operation genuinely can't be traced, consider `torch._dynamo.allow_in_graph` or restructuring user code
  94 | 
  95 | ### Backend Compiler Failures
  96 | 
  97 | `BackendCompilerFailed` means Inductor (or another backend) crashed during compilation.
  98 | 
  99 | **Diagnosis:**
 100 | ```bash
 101 | TORCHDYNAMO_REPRO_AFTER=aot TORCHDYNAMO_REPRO_LEVEL=2 python your_script.py
 102 | ```
 103 | 
 104 | This generates `minifier_launcher.py` that isolates the minimal failing graph.
 105 | 
 106 | **Key files:**
 107 | - `torch/_dynamo/repro/after_aot.py` -- repro/minifier for post-AOT failures
 108 | - `torch/_inductor/` -- the backend itself
 109 | 
 110 | **Fix approach:**
 111 | 1. Run the minifier to get a minimal reproduction
 112 | 2. Inspect the FX graph (`TORCH_COMPILE_DEBUG=1`) to understand what ops are involved
 113 | 3. Check if it's a lowering issue (`torch/_inductor/lowering.py`), scheduling issue, or codegen issue
 114 | 4. Look at the generated output code if the error is in codegen
 115 | 
 116 | ### Recompilation Issues
 117 | 
 118 | Excessive recompilation happens when guards are too specific, causing cache misses.
 119 | 
 120 | **Diagnosis:**
 121 | ```bash
 122 | TORCH_LOGS="recompiles,recompiles_verbose,guards" python your_script.py
 123 | ```
 124 | 
 125 | **Key config:**
 126 | - `torch._dynamo.config.recompile_limit` (default: 8)
 127 | - `torch._dynamo.config.fail_on_recompile_limit_hit` -- set to `True` to get a hard error
 128 | 
 129 | **Common causes:**
 130 | - Changing tensor shapes without marking them dynamic
 131 | - Python scalar values that change between calls
 132 | - Global state mutations between calls
 133 | 
 134 | **Fix approach:**
 135 | 1. Read the recompilation reason from logs
 136 | 2. Identify the failing guard
 137 | 3. Either mark the relevant dimension as dynamic with `torch._dynamo.mark_dynamic()` or fix the source of guard instability
 138 | 
 139 | ### Accuracy Issues
 140 | 
 141 | The compiled model produces different numerical results than eager mode.
 142 | 
 143 | **Diagnosis:**
 144 | ```bash
 145 | TORCHDYNAMO_REPRO_AFTER=aot TORCHDYNAMO_REPRO_LEVEL=4 python your_script.py
 146 | ```
 147 | 
 148 | This compares compiled vs. eager with an fp64 reference and dumps a repro if accuracy fails.
 149 | 
 150 | **Key utilities:**
 151 | - `torch/_dynamo/debug_utils.py` -- `same_two_models()`, `backend_accuracy_fails()`, `cast_to_fp64()`
 152 | - `torch._dynamo.config.repro_tolerance` (default: 1e-3)
 153 | 
 154 | **Fix approach:**
 155 | 1. Get the minimal failing graph from the minifier
 156 | 2. Compare eager vs. compiled output at fp64 precision
 157 | 3. Binary search through ops to find the diverging operation
 158 | 4. Check for known numerical issues (reduction order, fused kernels, dtype promotions)
 159 | 
 160 | ### Internal Dynamo Errors
 161 | 
 162 | `InternalTorchDynamoError` indicates a bug in Dynamo itself.
 163 | 
 164 | **Diagnosis:**
 165 | ```bash
 166 | TORCHDYNAMO_VERBOSE=1 python your_script.py
 167 | # or equivalently:
 168 | TORCH_LOGS="+dynamo" python your_script.py
 169 | ```
 170 | 
 171 | **Key files:**
 172 | - `torch/_dynamo/symbolic_convert.py` -- bytecode interpreter
 173 | - `torch/_dynamo/variables/` -- variable tracking system
 174 | - `torch/_dynamo/guards.py` -- guard generation
 175 | 
 176 | **Fix approach:**
 177 | 1. Get the full stack trace with `TORCHDYNAMO_VERBOSE=1`
 178 | 2. Identify which bytecode instruction or variable type caused the crash
 179 | 3. Create a minimal repro (the error message often includes a minifier path)
 180 | 4. Debug with `TORCHINDUCTOR_COMPILE_THREADS=1` and pdb if needed
 181 | 
 182 | ### Runtime Crashes
 183 | 
 184 | Segfaults and CUDA illegal memory access errors during execution of compiled code.
 185 | 
 186 | **Diagnosis (make crash deterministic):**
 187 | ```bash
 188 | PYTORCH_NO_CUDA_MEMORY_CACHING=1 CUDA_LAUNCH_BLOCKING=1 python your_script.py
 189 | ```
 190 | 
 191 | **For CUDA IMA, add NaN checks:**
 192 | ```bash
 193 | TORCHINDUCTOR_NAN_ASSERTS=1 python your_script.py
 194 | ```
 195 | 
 196 | **For Inductor-level sync debugging:**
 197 | ```python
 198 | torch._inductor.config.triton.debug_sync_kernel = True  # sync after every kernel
 199 | torch._inductor.config.triton.debug_sync_graph = True   # sync before/after graph
 200 | ```
 201 | 
 202 | **Fix approach:**
 203 | 1. Make the crash deterministic with `PYTORCH_NO_CUDA_MEMORY_CACHING=1 CUDA_LAUNCH_BLOCKING=1`
 204 | 2. Check if it's an input mismatch (shapes, devices, dtypes)
 205 | 3. Inspect the generated kernel code with `TORCH_LOGS="output_code"`
 206 | 4. Use `TORCHINDUCTOR_NAN_ASSERTS=1` to find the first kernel producing bad values
 207 | 5. Check for dynamic shapes issues (historically a common source of IMA)
 208 | 
 209 | ### Triton Kernel Failures
 210 | 
 211 | Triton assertion failures or index-out-of-bounds in generated kernels.
 212 | 
 213 | **Diagnosis:**
 214 | ```bash
 215 | TORCH_LOGS="output_code,schedule" python your_script.py
 216 | ```
 217 | 
 218 | **Key files:**
 219 | - `torch/_inductor/codegen/triton.py` -- Triton codegen
 220 | - `torch/_inductor/scheduler.py` -- kernel fusion decisions
 221 | 
 222 | **Fix approach:**
 223 | 1. Get the generated Triton kernel from `output_code` logs
 224 | 2. Check index computations for off-by-one or wrong stride calculations
 225 | 3. Look at the IR (`TORCH_COMPILE_DEBUG=1`) to trace back to the FX op
 226 | 4. Check if fusion decisions created invalid index combinations
 227 | 
 228 | ## Key Source Files
 229 | 
 230 | | File | Purpose |
 231 | |---|---|
 232 | | `torch/_dynamo/exc.py` | Exception hierarchy and error formatting |
 233 | | `torch/_dynamo/debug_utils.py` | Minifier support, accuracy checking, input serialization |
 234 | | `torch/_dynamo/repro/after_dynamo.py` | Repro/minifier for Dynamo-stage failures |
 235 | | `torch/_dynamo/repro/after_aot.py` | Repro/minifier for post-AOTAutograd failures |
 236 | | `torch/_dynamo/repro/aoti.py` | Repro/minifier for AOTI failures |
 237 | | `torch/_dynamo/config.py` | Dynamo config (repro levels, recompile limits) |
 238 | | `torch/_dynamo/variables/torch.py` | Torch function handling, tracing state functions |
 239 | | `torch/_dynamo/variables/higher_order_ops.py` | HOP tracing (cond, map, etc.) |
 240 | | `torch/_dynamo/symbolic_convert.py` | Bytecode interpreter, InstructionTranslator |
 241 | | `torch/_dynamo/convert_frame.py` | Frame compilation, `fullgraph_capture` entry point |
 242 | | `torch/_dynamo/functional_export.py` | New export tracer (`_dynamo_graph_capture_for_export`) |
 243 | | `torch/_dynamo/eval_frame.py` | `torch._dynamo.export`, `optimize_assert` |
 244 | | `torch/_export/_trace.py` | Export pipeline (`_export`, `_strict_export`, `_non_strict_export`, `_export_to_aten_ir`) |
 245 | | `torch/_export/utils.py` | `_compiling_state_context()` |
 246 | | `torch/compiler/__init__.py` | `is_compiling()`, `is_exporting()`, runtime flags |
 247 | | `torch/_higher_order_ops/cond.py` | `torch.cond` implementation and proxy tracing |
 248 | | `torch/_higher_order_ops/utils.py` | `reenter_make_fx` for HOP branch tracing |
 249 | | `torch/_inductor/config.py` | Inductor config (debug flags, trace settings) |
 250 | | `torch/_inductor/debug.py` | DebugContext, graph visualization, IR logging |
 251 | | `torch/_logging/_registrations.py` | All registered log aliases and artifacts |
 252 | 
 253 | ## Using the Minifier
 254 | 
 255 | The minifier reduces a failing graph to the smallest reproduction:
 256 | 
 257 | ```bash
 258 | # Step 1: Generate the minifier launcher
 259 | TORCHDYNAMO_REPRO_AFTER=aot TORCHDYNAMO_REPRO_LEVEL=2 python your_script.py
 260 | 
 261 | # Step 2: Run the minifier
 262 | python minifier_launcher.py minify
 263 | 
 264 | # Step 3: Run the minimized repro
 265 | python minifier_launcher.py run
 266 | ```
 267 | 
 268 | For accuracy issues, use level 4:
 269 | ```bash
 270 | TORCHDYNAMO_REPRO_AFTER=aot TORCHDYNAMO_REPRO_LEVEL=4 python your_script.py
 271 | ```
```


---
## .claude/skills/pyrefly-type-coverage/SKILL.md

```
   1 | ---
   2 | name: pyrefly-type-coverage
   3 | description: Migrate a file to use stricter Pyrefly type checking with annotations required for all functions, classes, and attributes.
   4 | ---
   5 | 
   6 | # Pyrefly Type Coverage Skill
   7 | 
   8 | This skill guides you through improving type coverage in Python files using Pyrefly, Meta's type checker. Follow this systematic process to add proper type annotations to files.
   9 | 
  10 | ## Prerequisites
  11 | - The file you're working on should be in a project with a `pyrefly.toml` configuration
  12 | 
  13 | ## Step-by-Step Process
  14 | 
  15 | ### Step 1: Remove Ignore Errors Directive
  16 | 
  17 | First, locate and remove any `pyre-ignore-all-errors` comments at the top of the file:
  18 | 
  19 | ```python
  20 | # REMOVE lines like these:
  21 | # pyre-ignore-all-errors
  22 | # pyre-ignore-all-errors[16,21,53,56]
  23 | # @lint-ignore-every PYRELINT
  24 | ```
  25 | 
  26 | These directives suppress type checking for the entire file and must be removed to enable proper type coverage.
  27 | 
  28 | ### Step 2: Add Entry to pyrefly.toml
  29 | 
  30 | Add a sub-config entry for stricter type checking. Open `pyrefly.toml` and add an entry following this pattern:
  31 | 
  32 | ```toml
  33 | [[sub-config]]
  34 | matches = "path/to/your/file.py"
  35 | [sub-config.errors]
  36 | implicit-import = false
  37 | implicit-any = true
  38 | ```
  39 | 
  40 | For directory-level coverage:
  41 | ```toml
  42 | [[sub-config]]
  43 | matches = "path/to/directory/**"
  44 | [sub-config.errors]
  45 | implicit-import = false
  46 | implicit-any = true
  47 | ```
  48 | 
  49 | You can also enable stricter options as needed:
  50 | ```toml
  51 | [[sub-config]]
  52 | matches = "path/to/your/file.py"
  53 | [sub-config.errors]
  54 | implicit-import = false
  55 | implicit-any = true
  56 | # Uncomment these for stricter checking:
  57 | # unannotated-attribute = true
  58 | # unannotated-parameter = true
  59 | # unannotated-return = true
  60 | ```
  61 | 
  62 | ### Step 3: Run Pyrefly to Identify Missing Coverage
  63 | 
  64 | Execute the type checker to see all type errors:
  65 | 
  66 | ```bash
  67 | pyrefly check <FILENAME>
  68 | ```
  69 | 
  70 | Example:
  71 | ```bash
  72 | pyrefly check torch/_dynamo/utils.py
  73 | ```
  74 | 
  75 | This will output a list of type errors with line numbers and descriptions. Common error types include:
  76 | - Missing return type annotations
  77 | - Missing parameter type annotations
  78 | - Incompatible types
  79 | - Missing attribute definitions
  80 | - Implicit `Any` usage
  81 | 
  82 | **CRITICAL**: Your goal is to resolve all errors. If you cannot resolve an error, you can use `# pyrefly: ignore[...]` to suppress but you should try to resolve the error first
  83 | 
  84 | ### Step 4: Add Type Annotations
  85 | 
  86 | Work through each error systematically:
  87 | 
  88 | 1. **Read the function/code carefully** - Understand what the function does
  89 | 2. **Examine usage patterns** - Look at how the function is called to understand expected types
  90 | 3. **Add appropriate annotations** - Add type hints based on your analysis
  91 | 
  92 | #### Common Annotation Patterns
  93 | 
  94 | **Function signatures:**
  95 | ```python
  96 | # Before
  97 | def process_data(items, callback):
  98 |     ...
  99 | 
 100 | # After
 101 | from collections.abc import Callable
 102 | def process_data(items: list[str], callback: Callable[[str], bool]) -> None:
 103 |     ...
 104 | ```
 105 | 
 106 | **Class attributes:**
 107 | ```python
 108 | # Before
 109 | class MyClass:
 110 |     def __init__(self):
 111 |         self.value = None
 112 |         self.items = []
 113 | 
 114 | # After
 115 | class MyClass:
 116 |     value: int | None
 117 |     items: list[str]
 118 | 
 119 |     def __init__(self) -> None:
 120 |         self.value = None
 121 |         self.items = []
 122 | ```
 123 | 
 124 | **Complex types:**
 125 | **CRITICAL**: use syntax for Python >3.10 and prefer collections.abc as opposed to
 126 | typing for better code standards.
 127 | 
 128 | **Critical**: For more advanced/generic types such as `TypeAlias`, `TypeVar`, `Generic`, `Protocol`, etc. use `typing_extensions`
 129 | 
 130 | ```python
 131 | 
 132 | # Optional values
 133 | def get_value(key: str) -> int | None: ...
 134 | 
 135 | # Union types
 136 | def process(value: str | int) -> str: ...
 137 | 
 138 | # Dict and List
 139 | def transform(data: dict[str, list[int]]) -> list[str]: ...
 140 | 
 141 | # Callable
 142 | from collections.abc import Callable
 143 | def apply(func: Callable[[int, int], int], a: int, b: int) -> int: ...
 144 | 
 145 | # TypeVar for generics
 146 | from typing_extensions import TypeVar
 147 | T = TypeVar('T')
 148 | def first(items: list[T]) -> T: ...
 149 | ```
 150 | 
 151 | **Using `# pyre-ignore` for specific lines:**
 152 | 
 153 | If a specific line is difficult to type correctly (e.g., dynamic metaprogramming), you can ignore just that line:
 154 | 
 155 | ```python
 156 | # pyrefly: ignore[attr-defined]
 157 | result = getattr(obj, dynamic_name)()
 158 | ```
 159 | 
 160 | **CRITICAL**: Avoid using `# pyre-ignore` unless it is necessary.
 161 | When possible, we can implement stubs, or refactor code to make it more type-safe.
 162 | 
 163 | ### Step 5: Iterate and Verify
 164 | 
 165 | After adding annotations:
 166 | 
 167 | 1. **Re-run pyrefly check** to verify errors are resolved:
 168 |    ```bash
 169 |    pyrefly check <FILENAME>
 170 |    ```
 171 | 
 172 | 2. **Fix any new errors** that may appear from the annotations you added
 173 | 
 174 | 3. **Repeat until clean** - Continue until pyrefly reports no errors
 175 | 
 176 | 
 177 | ### Step 6: Commit Changes
 178 | To keep type coverage PRs manageable, you should commit your change once finished with a file.
 179 | 
 180 | ## Tips for Success
 181 | 
 182 | 1. **Start with function signatures** - Return types and parameter types are usually the highest priority
 183 | 
 184 | 2. **Use `from __future__ import annotations`** - Add this at the top of the file for forward references:
 185 |    ```python
 186 |    from __future__ import annotations
 187 |    ```
 188 | 
 189 | 3. **Leverage type inference** - Pyrefly can infer many types; focus on function boundaries
 190 | 
 191 | 4. **Check existing type stubs** - For external libraries, check if type stubs exist
 192 | 
 193 | 5. **Use `typing_extensions` for newer features** - For compatibility:
 194 |    ```python
 195 |    from typing_extensions import TypeAlias, Self, ParamSpec
 196 |    ```
 197 | 
 198 | 6. **Document complex types with TypeAlias**:
 199 |    ```python
 200 |    from typing import Dict, List, TypeAlias
 201 | 
 202 |    ConfigType: TypeAlias = Dict[str, List[int]]
 203 | 
 204 |    def process_config(config: ConfigType) -> None: ...
 205 |    ```
 206 | 
 207 | ## Example Workflow
 208 | 
 209 | ```bash
 210 | # 1. Open the file and remove pyre-ignore-all-errors
 211 | # 2. Add entry to pyrefly.toml
 212 | 
 213 | # 3. Check initial errors
 214 | pyrefly check torch/my_module.py
 215 | 
 216 | # 4. Add annotations iteratively
 217 | 
 218 | # 5. Re-check after changes
 219 | pyrefly check torch/my_module.py
 220 | 
 221 | # 6. Repeat until clean
 222 | ```
```


---
## .claude/skills/scrub-issue/SKILL.md

```
   1 | ---
   2 | name: scrub-issue
   3 | disable-model-invocation: true
   4 | description: Fetch, analyze, reproduce, and minimize GitHub issue reproductions. Use when asked to check if an issue reproduces, minimize a repro, analyze a bug report, or scrub/triage an issue for reproducibility.
   5 | ---
   6 | 
   7 | # Minimize Issue Reproduction
   8 | 
   9 | Fetch a GitHub issue, evaluate whether it has a reasonable repro, check if it
  10 | still reproduces, and systematically minimize the repro to the smallest possible
  11 | self-contained script.
  12 | 
  13 | ## Tools
  14 | 
  15 | Assume the current environment is correct and run `python` directly. Only use
  16 | `conda run -n <env>` for version bisection (step 5a) where you need to
  17 | temporarily use a different environment. Use the Bash tool's `timeout`
  18 | parameter to enforce timeouts when running repro scripts.
  19 | 
  20 | - `gh issue view <NUMBER> --repo pytorch/pytorch` to fetch the issue body
  21 | - `gh issue view --comments <NUMBER> --repo pytorch/pytorch` to fetch comments
  22 | - `python <script>` to run repro scripts
  23 | - `gh issue comment <NUMBER> --repo pytorch/pytorch --body <BODY>` to comment
  24 | - `gh issue edit <NUMBER> --repo pytorch/pytorch --add-label <LABEL>` to add labels
  25 | 
  26 | Multiple `gh issue edit` flags can be combined in a single command (e.g.
  27 | `--add-label "bug,help wanted" --add-assignee "@me"`). Prefer batching
  28 | edits into one command to minimize API calls and reduce the chance of
  29 | auto-subscribing to notifications.
  30 | 
  31 | ### Preserving notification subscription state
  32 | 
  33 | Modifying an issue (commenting, adding labels) auto-subscribes you to
  34 | notifications. Use `tools/stale_issues.py` to save and restore subscription
  35 | state:
  36 | 
  37 | 1. **Before the first modification**, save the current state. This can be
  38 |    run in parallel with fetching the issue body/comments, but it must
  39 |    **complete** before any `gh issue edit`, `gh issue comment`, or
  40 |    `gh issue close` command is executed:
  41 |    ```
  42 |    python tools/stale_issues.py subscription save <NUMBER>
  43 |    ```
  44 | 2. **After the last modification**, restore the saved state — **unless the
  45 |    issue was closed** (via `gh issue close`), in which case skip the restore
  46 |    so the user stays subscribed to follow any responses to the closure. The
  47 |    restore must be the very last GitHub API call — do not run it in the
  48 |    background or in parallel with any `gh issue edit` or `gh issue comment`
  49 |    commands:
  50 |    ```
  51 |    python tools/stale_issues.py subscription restore <NUMBER>
  52 |    ```
  53 | 
  54 | If either the save or restore command fails, warn the user and continue
  55 | without the save/restore mechanism.
  56 | 
  57 | **Important**: Never run `gh issue edit`, `gh issue comment`, `gh issue close`,
  58 | or subscription save/restore commands in the background. These must all run in
  59 | the foreground so their completion can be verified before proceeding.
  60 | If commenting or editing fails because the issue is locked, report this to the
  61 | user and skip the modification.
  62 | 
  63 | ### Security review checklist
  64 | 
  65 | Before running any repro code, check for the following concerns:
  66 | 
  67 | - Network requests to untrusted URLs (requests, urllib, curl, wget)
  68 | - File operations outside `/tmp/`
  69 | - Shell command execution (os.system, subprocess, eval, exec) — but
  70 |   `subprocess` used to launch `torchrun` or `mp.spawn` for distributed repros
  71 |   is expected and not a concern
  72 | - Downloading or loading external files (model weights, pickled objects, data
  73 |   files) — especially `torch.load` on untrusted `.pt`/`.pth` files
  74 | - Obfuscated code (base64-encoded strings, encoded bytes, unusual escapes)
  75 | - Package installation (pip install, conda install)
  76 | - Environment variable manipulation that could affect the host system — but
  77 |   setting `MASTER_ADDR`, `MASTER_PORT`, `RANK`, `WORLD_SIZE`,
  78 |   `CUDA_VISIBLE_DEVICES`, or other standard PyTorch/CUDA env vars is expected
  79 |   and not a concern
  80 | 
  81 | If any of these are present, explain the concern to the user and ask whether
  82 | to proceed, skip, or modify the repro to remove the risky parts. If the user
  83 | chooses to skip, still refresh the `triaged` label timestamp (remove and
  84 | re-add, or just add if not present) before reporting that the analysis is
  85 | finished.
  86 | 
  87 | Even if the repro passes the checklist above, check whether the author of the
  88 | repro code is a PyTorch collaborator by running
  89 | `python tools/stale_issues.py collaborator-check <username>`. If the command
  90 | exits with a non-zero status (user is not a collaborator), show the repro code
  91 | to the user and ask them to verify it is safe to run before executing it.
  92 | 
  93 | ## Steps
  94 | 
  95 | ### 1) Fetch the issue
  96 | 
  97 | Fetch the issue body and comments in parallel. Identify the reported repro
  98 | script and error. If multiple repros are present, prefer the most recent one
  99 | from the original poster. If a commenter has posted a strictly shorter and
 100 | more self-contained repro that doesn't require additional context from the
 101 | issue description, prefer that one. Note which repro you selected. If the
 102 | repro code is only present in screenshots or images rather than copyable text,
 103 | stop and report this to the user.
 104 | 
 105 | ### 2) Check if the issue is actionable
 106 | 
 107 | Before investing effort in reproduction, check whether the issue is actionable.
 108 | **Do not proceed to later steps** if any of the following apply:
 109 | 
 110 | - **Already closed or resolved** in comments. Report to the user and stop.
 111 |   Do not modify labels on closed issues.
 112 | - **Duplicate** of another issue (linked or obviously the same bug)
 113 | - **Not a bug report** (feature request, question, discussion, refactoring /
 114 |   code cleanup task). If the issue is a feature request and doesn't already
 115 |   have the `feature` label, add it via `gh issue edit`. If the issue is a
 116 |   better-engineering / refactoring task and doesn't already have the
 117 |   `better-engineering` label, add it via `gh issue edit`. If the issue
 118 |   includes a repro script that demonstrates the current behavior, apply the
 119 |   security review checklist first, then run it to verify the behavior
 120 |   persists. If the repro needed to be modernized (e.g. updated imports for
 121 |   renamed APIs), or if you verified that the behavior still persists, comment
 122 |   on the issue with the findings and updated repro. After adding any
 123 |   applicable labels (and optionally running/commenting on a repro), report
 124 |   the analysis to the user and do not proceed to later steps.
 125 | - **Tracking/meta issue** (umbrella issue tracking multiple bugs, burn-down
 126 |   lists, improvement proposals without a specific repro). If the issue doesn't
 127 |   already have the `tracker` label, add it via `gh issue edit`. Then stop and
 128 |   report to the user.
 129 | - **Requires unavailable hardware** (specific GPU models, TPUs, multi-node) with
 130 |   no path to simplify. Note: CUDA is available on the current machine, so
 131 |   single-GPU CUDA repros can be run directly.
 132 | 
 133 | For non-actionable issues that are old (more than ~1 year), have no assignees,
 134 | no recent progress, and are underspecified or lack concrete motivation, suggest
 135 | closing them as "not planned" (`gh issue close --reason "not planned"`) with a
 136 | comment explaining the rationale. Ask the user before closing.
 137 | 
 138 | If the issue is not actionable and no GitHub-visible modification was made (no
 139 | label added, no comment posted — saving subscription state does not count),
 140 | refresh the `triaged` label to update the issue's
 141 | "last updated" timestamp. A single `gh issue edit` with both `--remove-label`
 142 | and `--add-label` doesn't work because the remove and add cancel each other
 143 | out. Instead, chain both edits in a single Bash tool call:
 144 | `gh issue edit ... --remove-label triaged && gh issue edit ... --add-label triaged`.
 145 | If the issue doesn't have the `triaged` label, just add it.
 146 | 
 147 | Then summarize why the issue is not actionable. If a label or other update was
 148 | made, just report that the analysis is finished. Only ask the user how to
 149 | proceed if no update was made and the situation is ambiguous. Always ask the
 150 | user before closing an issue.
 151 | 
 152 | ### 3) Analyze the repro
 153 | 
 154 | Evaluate whether the issue has a reasonable repro:
 155 | 
 156 | - Is there a code snippet that can be run?
 157 | - Are the dependencies available (CUDA, distributed, specific hardware)?
 158 |   Note: `torch.distributed` repros often don't require special hardware — they
 159 |   can be launched with `torchrun --nproc_per_node=1` or `mp.spawn` on a single
 160 |   machine.
 161 | - Is the expected error described?
 162 | - Is the repro self-contained or does it need external data/models?
 163 | 
 164 | If there is no repro code at all, or the issue is missing critical info (no
 165 | error message, no description of expected vs actual behavior), add the
 166 | `needs reproduction` label (if not already present) via `gh issue edit`, then
 167 | stop and report to the user. Do not attempt to write a repro from the
 168 | description without being asked.
 169 | 
 170 | Conversely, if the issue already has the `needs reproduction` label but does
 171 | have a valid repro, remove the label via `gh issue edit --remove-label
 172 | "needs reproduction"`.
 173 | 
 174 | Apply the security review checklist (see above) to the repro before running it.
 175 | 
 176 | If the repro requires third-party packages that are not installed (e.g.
 177 | `transformers`, `torchvision`, `numpy`), stop and ask the user how to proceed
 178 | rather than installing them yourself.
 179 | 
 180 | Summarize your assessment before proceeding.
 181 | 
 182 | ### 4) Check for recent verification
 183 | 
 184 | If a comment from the last six months already confirms the issue still
 185 | reproduces (with a matching error and a reasonable repro), stop and ask the
 186 | user whether they want to re-verify or skip ahead to minimization.
 187 | 
 188 | ### 5) Check if it still reproduces
 189 | 
 190 | Extract the repro code into a temporary file under `/tmp/` and run it with a
 191 | timeout of 120 seconds. For repros involving `torch.compile` that call compile
 192 | multiple times in the same process, add `torch._dynamo.reset()` between
 193 | invocations to reset in-memory Dynamo state. This is unnecessary for scripts
 194 | that compile once and exit.
 195 | 
 196 | If the script times out, consider whether a hang is the reported bug or an
 197 | unrelated issue, and report to the user.
 198 | 
 199 | Record the PyTorch version before running
 200 | (`python -c "import torch; print(torch.__version__)"`) for inclusion in the
 201 | report.
 202 | 
 203 | Check both the exit code and output to determine the result. An exit code > 128
 204 | indicates the process was killed by a signal (e.g. segfault = 139, OOM kill =
 205 | 137) — this is a valid crash reproduction even without a Python traceback. If
 206 | the repro crashes with a CUDA out-of-memory error and OOM is not the reported
 207 | bug, try reducing tensor sizes before concluding it doesn't reproduce. For
 208 | correctness bugs (wrong numerical results rather than crashes), the repro
 209 | should include an assertion that fails when the bug is present. If the
 210 | original repro only prints output without asserting, add a simple assertion
 211 | based on the expected behavior described in the issue (e.g.
 212 | `assert torch.allclose(actual, expected)`) so the repro has a clear
 213 | pass/fail signal.
 214 | 
 215 | If the result is inconsistent across runs, run 3-5 times to assess flakiness.
 216 | For non-deterministic bugs, try setting `PYTHONHASHSEED=0` and a fixed
 217 | `torch.manual_seed` to stabilize reproduction. Report the success/failure ratio
 218 | to the user. Flaky repros are still valid bugs — note the flakiness in the
 219 | issue comment (step 8) and include the success/failure ratio.
 220 | 
 221 | Three possible outcomes (to determine which outcome applies, match on the
 222 | exception class and a distinctive substring of the error message — the
 223 | substring should be specific enough to identify the bug, e.g.
 224 | `RuntimeError: expected scalar type Float` rather than just `RuntimeError`):
 225 | 
 226 | - **Same error as reported**: the bug still reproduces. Continue to step 6.
 227 | - **No error (passes)**: the bug may have been fixed. Try to identify the
 228 |   fixing PR (see step 5a), then report to the user. The issue will be closed
 229 |   in step 8.
 230 | - **Different error**: distinguish between setup issues (missing import, renamed
 231 |   API) that can be fixed and genuinely different bugs. If the error is due to
 232 |   API changes between the reported version and the current version (renamed
 233 |   functions, moved modules, changed signatures), adapt the repro to use the
 234 |   current API while preserving the original intent. If the error is unclear,
 235 |   consider re-running with `TORCH_LOGS=+dynamo` or other relevant logging flags
 236 |   for more diagnostic output. Report genuinely different errors to the user.
 237 | 
 238 | ### 5a) Identify when and how it was fixed
 239 | 
 240 | When the bug no longer reproduces, try to determine which version fixed it and
 241 | which PR introduced the fix.
 242 | 
 243 | **Version bisection**: Check if conda environments named `pytorch-<version>`
 244 | (e.g. `pytorch-2.6`, `pytorch-2.8`) are available (`conda env list | grep
 245 | pytorch-`). If they exist, binary-search across them to find the first version
 246 | where the bug is fixed. Run from `/tmp` in a subshell and clear `PYTHONPATH`
 247 | to avoid picking up the local source tree (which would cause `torch._C` import
 248 | errors): `(cd /tmp && PYTHONPATH= conda run -n pytorch-<version> python
 249 | /tmp/repro_....py)`. To speed up bisection, pick 2-3 evenly-spaced probe
 250 | points from the candidate range and test them in parallel each round (e.g.
 251 | if candidates are 2.2 through 2.8, test 2.4 and 2.6 simultaneously to split
 252 | the range into thirds). If no versioned conda environments are
 253 | available, skip bisection and just report that the bug no longer reproduces on
 254 | the current version.
 255 | 
 256 | **PR identification**: Try to find the specific PR that fixed the bug. Use
 257 | version control blame on the relevant fix code to find the changeset, then look
 258 | up the commit message for the PR number (format `(#NNNNN)`). Alternatively,
 259 | search version control history for commits touching the relevant file with a
 260 | related keyword. If this doesn't yield a clear answer quickly, just report the
 261 | version — don't spend extra time on PR identification.
 262 | 
 263 | ### 6) Minimize the repro
 264 | 
 265 | Save the original working repro to `/tmp/repro_<issue_number>_original.py`
 266 | before making any changes.
 267 | 
 268 | First, assess whether the repro is already reasonably minimal. Only minimize if
 269 | the repro has significant unnecessary complexity (large models, unused code
 270 | paths, unnecessary dependencies, etc.). When counting complexity, don't count
 271 | irreducible boilerplate — e.g. a tensor subclass definition that only contains
 272 | the required dunder methods (`__new__`, `__init__`, `__torch_dispatch__`,
 273 | `__tensor_flatten__`, `__tensor_unflatten__`) is not reducible even if it's
 274 | 20+ lines. Focus on whether the trigger code and model/setup complexity can
 275 | be meaningfully reduced. If the only possible "simplifications" are cosmetic
 276 | (inlining variables, removing `__repr__`), skip minimization.
 277 | 
 278 | Systematically reduce the repro by testing whether each simplification still
 279 | triggers the same error. Use a shorter timeout (30-60 seconds) during
 280 | minimization since simplified repros should run faster. Run multiple candidate
 281 | simplifications in parallel when they are independent (i.e. they modify
 282 | non-overlapping parts of the code and neither depends on what the other
 283 | removes).
 284 | 
 285 | **Reduction strategies (apply in roughly this order):**
 286 | 
 287 | 1. **Remove unnecessary imports and setup** (distributed init, env vars, logging)
 288 | 2. **Shrink the model** (replace large modules with minimal equivalents)
 289 | 3. **Remove the class/module wrapper** if a bare function suffices
 290 | 4. **Reduce tensor sizes** (large dims → small dims like 4 or 8)
 291 | 5. **Remove device/dtype requirements** (try CPU and float32 first)
 292 | 6. **Simplify the computation** (replace complex ops with minimal ones that still trigger the bug)
 293 | 7. **Remove unnecessary control flow** (branches, loops, conditions)
 294 | 8. **Try simpler backends** (e.g. `aot_eager` instead of inductor) if the bug is not backend-specific
 295 | 
 296 | After each round, verify the error still reproduces — same exception class and
 297 | a distinctive error message substring as described in step 5 (minor traceback
 298 | differences are fine). For correctness bugs, preserve the assertion that demonstrates the
 299 | wrong result and verify it still shows the same incorrect behavior. When merging multiple successful parallel simplifications, verify
 300 | the combined result still reproduces since independent simplifications can
 301 | interact. Stop minimizing when the repro is under ~20 lines of non-blank
 302 | non-import code, or when two consecutive rounds (where a round is one full
 303 | pass through the applicable reduction strategies) fail to simplify further.
 304 | 
 305 | ### 7) Apply trivial fixes
 306 | 
 307 | If the analysis reveals a trivial fix (e.g. removing a stale `xfailIfTorchDynamo`
 308 | or `expectedFailure` annotation from a test because the underlying issue is
 309 | fixed), report the fix to the user and ask whether to apply it. Do not modify
 310 | source files without the user's approval. In step 8, mention the fix
 311 | regardless of whether it was applied or declined.
 312 | 
 313 | ### 8) Report findings
 314 | 
 315 | If the repro was minimized, save it to `/tmp/repro_<issue_number>.py` so the
 316 | user can run it directly.
 317 | 
 318 | Present findings to the user including:
 319 | - Whether the bug still reproduces (and on what PyTorch version)
 320 | - The fixing PR, if identified (only if the bug no longer reproduces)
 321 | - The minimized repro script (only if we minimized it)
 322 | - The necessary conditions to trigger the bug
 323 | - Any trivial fix identified in step 7 (whether applied or not)
 324 | - Recommended next action (e.g. "still a valid bug", "appears fixed", "needs
 325 |   more info from reporter")
 326 | 
 327 | After presenting findings, always comment on the issue with the results.
 328 | Keep the comment concise — don't repeat information already on the issue.
 329 | Only include a repro if it was materially changed from the original (e.g.
 330 | minimized, modernized imports, fixed to run on current API). Only include
 331 | trigger conditions if they are new findings not already discussed in prior
 332 | comments. If the only finding is "still reproduces" or "no longer reproduces",
 333 | a short comment is sufficient.
 334 | 
 335 | ```
 336 | This issue [still reproduces / no longer reproduces] on PyTorch <version>.
 337 | 
 338 | [If fixed and PR identified:]
 339 | Fixed by #NNNNN.
 340 | 
 341 | [If minimized or modernized — only include repro if changed from original:]
 342 | Minimized repro:
 343 | 
 344 | \`\`\`python
 345 | <repro script>
 346 | \`\`\`
 347 | 
 348 | [Only if new findings about trigger conditions:]
 349 | All of the following are necessary to trigger the bug:
 350 | - <condition 1>
 351 | - <condition 2>
 352 | 
 353 | (Analysis done by Claude.)
 354 | ```
 355 | 
 356 | If the bug no longer reproduces, after commenting close the issue:
 357 | `gh issue close <NUMBER> --repo pytorch/pytorch --reason completed --comment "Closing as this was fixed in PyTorch <version>."`.
 358 | Do not ask the user before closing — fixed bugs should always be closed.
 359 | 
 360 | After the last GitHub modification, restore the notification subscription
 361 | state (see "Preserving notification subscription state" above) — unless the
 362 | issue was closed, in which case skip the restore.
```


---
## .claude/skills/skill-writer/SKILL.md

```
   1 | ---
   2 | name: skill-writer
   3 | description: Guide users through creating Agent Skills for Claude Code. Use when the user wants to create, write, author, or design a new Skill, or needs help with SKILL.md files, frontmatter, or skill structure.
   4 | ---
   5 | 
   6 | # Skill Writer
   7 | 
   8 | This Skill helps you create well-structured Agent Skills for Claude Code that follow best practices and validation requirements.
   9 | 
  10 | ## When to use this Skill
  11 | 
  12 | Use this Skill when:
  13 | - Creating a new Agent Skill
  14 | - Writing or updating SKILL.md files
  15 | - Designing skill structure and frontmatter
  16 | - Troubleshooting skill discovery issues
  17 | - Converting existing prompts or workflows into Skills
  18 | 
  19 | ## Instructions
  20 | 
  21 | ### Step 1: Determine Skill scope
  22 | 
  23 | First, understand what the Skill should do:
  24 | 
  25 | 1. **Ask clarifying questions**:
  26 |    - What specific capability should this Skill provide?
  27 |    - When should Claude use this Skill?
  28 |    - What tools or resources does it need?
  29 |    - Is this for personal use or team sharing?
  30 | 
  31 | 2. **Keep it focused**: One Skill = one capability
  32 |    - Good: "PDF form filling", "Excel data analysis"
  33 |    - Too broad: "Document processing", "Data tools"
  34 | 
  35 | ### Step 2: Choose Skill location
  36 | 
  37 | Determine where to create the Skill:
  38 | 
  39 | **Personal Skills** (`~/.claude/skills/`):
  40 | - Individual workflows and preferences
  41 | - Experimental Skills
  42 | - Personal productivity tools
  43 | 
  44 | **Project Skills** (`.claude/skills/`):
  45 | - Team workflows and conventions
  46 | - Project-specific expertise
  47 | - Shared utilities (committed to git)
  48 | 
  49 | ### Step 3: Create Skill structure
  50 | 
  51 | Create the directory and files:
  52 | 
  53 | ```bash
  54 | # Personal
  55 | mkdir -p ~/.claude/skills/skill-name
  56 | 
  57 | # Project
  58 | mkdir -p .claude/skills/skill-name
  59 | ```
  60 | 
  61 | For multi-file Skills:
  62 | ```
  63 | skill-name/
  64 | ├── SKILL.md (required)
  65 | ├── reference.md (optional)
  66 | ├── examples.md (optional)
  67 | ├── scripts/
  68 | │   └── helper.py (optional)
  69 | └── templates/
  70 |     └── template.txt (optional)
  71 | ```
  72 | 
  73 | ### Step 4: Write SKILL.md frontmatter
  74 | 
  75 | Create YAML frontmatter with required fields:
  76 | 
  77 | ```yaml
  78 | ---
  79 | name: skill-name
  80 | description: Brief description of what this does and when to use it
  81 | ---
  82 | ```
  83 | 
  84 | **Field requirements**:
  85 | 
  86 | - **name**:
  87 |   - Lowercase letters, numbers, hyphens only
  88 |   - Max 64 characters
  89 |   - Must match directory name
  90 |   - Good: `pdf-processor`, `git-commit-helper`
  91 |   - Bad: `PDF_Processor`, `Git Commits!`
  92 | 
  93 | - **description**:
  94 |   - Max 1024 characters
  95 |   - Include BOTH what it does AND when to use it
  96 |   - Use specific trigger words users would say
  97 |   - Mention file types, operations, and context
  98 | 
  99 | **Optional frontmatter fields**:
 100 | 
 101 | - **allowed-tools**: Restrict tool access (comma-separated list)
 102 |   ```yaml
 103 |   allowed-tools: Read, Grep, Glob
 104 |   ```
 105 |   Use for:
 106 |   - Read-only Skills
 107 |   - Security-sensitive workflows
 108 |   - Limited-scope operations
 109 | 
 110 | ### Step 5: Write effective descriptions
 111 | 
 112 | The description is critical for Claude to discover your Skill.
 113 | 
 114 | **Formula**: `[What it does] + [When to use it] + [Key triggers]`
 115 | 
 116 | **Examples**:
 117 | 
 118 | ✅ **Good**:
 119 | ```yaml
 120 | description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
 121 | ```
 122 | 
 123 | ✅ **Good**:
 124 | ```yaml
 125 | description: Analyze Excel spreadsheets, create pivot tables, and generate charts. Use when working with Excel files, spreadsheets, or analyzing tabular data in .xlsx format.
 126 | ```
 127 | 
 128 | ❌ **Too vague**:
 129 | ```yaml
 130 | description: Helps with documents
 131 | description: For data analysis
 132 | ```
 133 | 
 134 | **Tips**:
 135 | - Include specific file extensions (.pdf, .xlsx, .json)
 136 | - Mention common user phrases ("analyze", "extract", "generate")
 137 | - List concrete operations (not generic verbs)
 138 | - Add context clues ("Use when...", "For...")
 139 | 
 140 | ### Step 6: Structure the Skill content
 141 | 
 142 | Use clear Markdown sections:
 143 | 
 144 | ```markdown
 145 | # Skill Name
 146 | 
 147 | Brief overview of what this Skill does.
 148 | 
 149 | ## Quick start
 150 | 
 151 | Provide a simple example to get started immediately.
 152 | 
 153 | ## Instructions
 154 | 
 155 | Step-by-step guidance for Claude:
 156 | 1. First step with clear action
 157 | 2. Second step with expected outcome
 158 | 3. Handle edge cases
 159 | 
 160 | ## Examples
 161 | 
 162 | Show concrete usage examples with code or commands.
 163 | 
 164 | ## Best practices
 165 | 
 166 | - Key conventions to follow
 167 | - Common pitfalls to avoid
 168 | - When to use vs. not use
 169 | 
 170 | ## Requirements
 171 | 
 172 | List any dependencies or prerequisites:
 173 | ```bash
 174 | pip install package-name
 175 | ```
 176 | 
 177 | ## Advanced usage
 178 | 
 179 | For complex scenarios, see [reference.md](reference.md).
 180 | ```
 181 | 
 182 | ### Step 7: Add supporting files (optional)
 183 | 
 184 | Create additional files for progressive disclosure:
 185 | 
 186 | **reference.md**: Detailed API docs, advanced options
 187 | **examples.md**: Extended examples and use cases
 188 | **scripts/**: Helper scripts and utilities
 189 | **templates/**: File templates or boilerplate
 190 | 
 191 | Reference them from SKILL.md:
 192 | ```markdown
 193 | For advanced usage, see [reference.md](reference.md).
 194 | 
 195 | Run the helper script:
 196 | \`\`\`bash
 197 | python scripts/helper.py input.txt
 198 | \`\`\`
 199 | ```
 200 | 
 201 | ### Step 8: Validate the Skill
 202 | 
 203 | Check these requirements:
 204 | 
 205 | ✅ **File structure**:
 206 | - [ ] SKILL.md exists in correct location
 207 | - [ ] Directory name matches frontmatter `name`
 208 | 
 209 | ✅ **YAML frontmatter**:
 210 | - [ ] Opening `---` on line 1
 211 | - [ ] Closing `---` before content
 212 | - [ ] Valid YAML (no tabs, correct indentation)
 213 | - [ ] `name` follows naming rules
 214 | - [ ] `description` is specific and < 1024 chars
 215 | 
 216 | ✅ **Content quality**:
 217 | - [ ] Clear instructions for Claude
 218 | - [ ] Concrete examples provided
 219 | - [ ] Edge cases handled
 220 | - [ ] Dependencies listed (if any)
 221 | 
 222 | ✅ **Testing**:
 223 | - [ ] Description matches user questions
 224 | - [ ] Skill activates on relevant queries
 225 | - [ ] Instructions are clear and actionable
 226 | 
 227 | ### Step 9: Test the Skill
 228 | 
 229 | 1. **Restart Claude Code** (if running) to load the Skill
 230 | 
 231 | 2. **Ask relevant questions** that match the description:
 232 |    ```
 233 |    Can you help me extract text from this PDF?
 234 |    ```
 235 | 
 236 | 3. **Verify activation**: Claude should use the Skill automatically
 237 | 
 238 | 4. **Check behavior**: Confirm Claude follows the instructions correctly
 239 | 
 240 | ### Step 10: Debug if needed
 241 | 
 242 | If Claude doesn't use the Skill:
 243 | 
 244 | 1. **Make description more specific**:
 245 |    - Add trigger words
 246 |    - Include file types
 247 |    - Mention common user phrases
 248 | 
 249 | 2. **Check file location**:
 250 |    ```bash
 251 |    ls ~/.claude/skills/skill-name/SKILL.md
 252 |    ls .claude/skills/skill-name/SKILL.md
 253 |    ```
 254 | 
 255 | 3. **Validate YAML**:
 256 |    ```bash
 257 |    cat SKILL.md | head -n 10
 258 |    ```
 259 | 
 260 | 4. **Run debug mode**:
 261 |    ```bash
 262 |    claude --debug
 263 |    ```
 264 | 
 265 | ## Common patterns
 266 | 
 267 | ### Read-only Skill
 268 | 
 269 | ```yaml
 270 | ---
 271 | name: code-reader
 272 | description: Read and analyze code without making changes. Use for code review, understanding codebases, or documentation.
 273 | allowed-tools: Read, Grep, Glob
 274 | ---
 275 | ```
 276 | 
 277 | ### Script-based Skill
 278 | 
 279 | ```yaml
 280 | ---
 281 | name: data-processor
 282 | description: Process CSV and JSON data files with Python scripts. Use when analyzing data files or transforming datasets.
 283 | ---
 284 | 
 285 | # Data Processor
 286 | 
 287 | ## Instructions
 288 | 
 289 | 1. Use the processing script:
 290 | \`\`\`bash
 291 | python scripts/process.py input.csv --output results.json
 292 | \`\`\`
 293 | 
 294 | 2. Validate output with:
 295 | \`\`\`bash
 296 | python scripts/validate.py results.json
 297 | \`\`\`
 298 | ```
 299 | 
 300 | ### Multi-file Skill with progressive disclosure
 301 | 
 302 | ```yaml
 303 | ---
 304 | name: api-designer
 305 | description: Design REST APIs following best practices. Use when creating API endpoints, designing routes, or planning API architecture.
 306 | ---
 307 | 
 308 | # API Designer
 309 | 
 310 | Quick start: See [examples.md](examples.md)
 311 | 
 312 | Detailed reference: See [reference.md](reference.md)
 313 | 
 314 | ## Instructions
 315 | 
 316 | 1. Gather requirements
 317 | 2. Design endpoints (see examples.md)
 318 | 3. Document with OpenAPI spec
 319 | 4. Review against best practices (see reference.md)
 320 | ```
 321 | 
 322 | ## Best practices for Skill authors
 323 | 
 324 | 1. **One Skill, one purpose**: Don't create mega-Skills
 325 | 2. **Specific descriptions**: Include trigger words users will say
 326 | 3. **Clear instructions**: Write for Claude, not humans
 327 | 4. **Concrete examples**: Show real code, not pseudocode
 328 | 5. **List dependencies**: Mention required packages in description
 329 | 6. **Test with teammates**: Verify activation and clarity
 330 | 7. **Version your Skills**: Document changes in content
 331 | 8. **Use progressive disclosure**: Put advanced details in separate files
 332 | 
 333 | ## Validation checklist
 334 | 
 335 | Before finalizing a Skill, verify:
 336 | 
 337 | - [ ] Name is lowercase, hyphens only, max 64 chars
 338 | - [ ] Description is specific and < 1024 chars
 339 | - [ ] Description includes "what" and "when"
 340 | - [ ] YAML frontmatter is valid
 341 | - [ ] Instructions are step-by-step
 342 | - [ ] Examples are concrete and realistic
 343 | - [ ] Dependencies are documented
 344 | - [ ] File paths use forward slashes
 345 | - [ ] Skill activates on relevant queries
 346 | - [ ] Claude follows instructions correctly
 347 | 
 348 | ## Troubleshooting
 349 | 
 350 | **Skill doesn't activate**:
 351 | - Make description more specific with trigger words
 352 | - Include file types and operations in description
 353 | - Add "Use when..." clause with user phrases
 354 | 
 355 | **Multiple Skills conflict**:
 356 | - Make descriptions more distinct
 357 | - Use different trigger words
 358 | - Narrow the scope of each Skill
 359 | 
 360 | **Skill has errors**:
 361 | - Check YAML syntax (no tabs, proper indentation)
 362 | - Verify file paths (use forward slashes)
 363 | - Ensure scripts have execute permissions
 364 | - List all dependencies
 365 | 
 366 | ## Examples
 367 | 
 368 | See the documentation for complete examples:
 369 | - Simple single-file Skill (commit-helper)
 370 | - Skill with tool permissions (code-reviewer)
 371 | - Multi-file Skill (pdf-processing)
 372 | 
 373 | ## Output format
 374 | 
 375 | When creating a Skill, I will:
 376 | 
 377 | 1. Ask clarifying questions about scope and requirements
 378 | 2. Suggest a Skill name and location
 379 | 3. Create the SKILL.md file with proper frontmatter
 380 | 4. Include clear instructions and examples
 381 | 5. Add supporting files if needed
 382 | 6. Provide testing instructions
 383 | 7. Validate against all requirements
 384 | 
 385 | The result will be a complete, working Skill that follows all best practices and validation rules.
```


---
## .claude/skills/triaging-issues/README.md

```
   1 | ## Summary
   2 | 
   3 | This is a skill for auto-triaging issues. This is the human side of things :)
   4 | There are 4 pieces to this skill;
   5 | 
   6 | 1. `SKILL.md` this is the main description of what to do/ directions to follow. If you notice a weird anti pattern in triaging
   7 | this is the file you should update. The basic workflow is that there is a static list of labels in `labels.json` that the agent will read w/ their descriptions in order to make decisions. *NOTE* This is static and if new labels are added to `pytorch/pytorch` we should
   8 | bump this list w/ their description. I made this static because the full set of labels is too big/quite stale. And I wanted to add more color to certain descriptions. The mechanics for actually interacting w/ gh issues is through the official mcp server. For V1, we always apply
   9 | `bot-triaged` whenever any triage action is taken; you can filter those decisions here: https://fburl.com/pt-bot-triaged
  10 | 2. `templates.json`: This is basically where we want to put canned responses. It includes `redirect_to_forum` (for usage questions) and
  11 | `request_more_info` (when classification is unclear). There are likely others we should add here as we notice more patterns.
  12 | 3. There are hooks in `/scripts`: a pre-hook (`validate_labels.py`) that filters out labels we never want the bot to add, and a post-hook (`add_bot_triaged.py`) that automatically applies `bot-triaged` after any issue mutation.
  13 | 4. The gh action uses a **two-stage workflow** to support issues opened by OSS users:
  14 |    - **Stage 1** (`.github/workflows/claude-issue-triage.yml`): Triggers on `issues: opened`, captures the issue number, and uploads it as an artifact. This stage has no protected environment, so OSS actors can run it.
  15 |    - **Stage 2** (`.github/workflows/claude-issue-triage-run.yml`): Triggers on `workflow_run` completion of Stage 1. Runs in the protected `bedrock` environment with AWS/Bedrock access. Downloads the artifact, reads the issue number, and runs the actual triage.
  16 | 
  17 |    **Why two stages?** GitHub environment protection blocks jobs before they start if the triggering actor isn't authorized. By using `workflow_run`, Stage 2 is triggered by GitHub itself (trusted context), allowing it to enter the protected environment regardless of who opened the issue.  We use sonnet-4.5, since from testing it is much cheaper and appears to do a more than adequate job at triaging.
  18 | 5. To disable the flow, disable the GitHub Actions workflow in the repo settings or remove/disable `.github/workflows/claude-issue-triage.yml`.
  19 | 6. If you would like to test updates before committing them upstream to pytorch, you can do that here: https://github.com/pytorch/ciforge @lint-ignore
```


---
## .claude/skills/triaging-issues/SKILL.md

```
   1 | ---
   2 | name: triaging-issues
   3 | description: Triages GitHub issues by routing to oncall teams, applying labels, and closing questions. Use when processing new PyTorch issues or when asked to triage an issue.
   4 | hooks:
   5 |   PreToolUse:
   6 |     - matcher: "mcp__github__issue_write|mcp__github__update_issue"
   7 |       hooks:
   8 |         - type: command
   9 |           command: "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/skills/triaging-issues/scripts/validate_labels.py"
  10 |   PostToolUse:
  11 |     - matcher: "mcp__github__issue_write|mcp__github__update_issue|mcp__github__add_issue_comment|mcp__github__transfer_issue"
  12 |       hooks:
  13 |         - type: command
  14 |           command: "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/skills/triaging-issues/scripts/add_bot_triaged.py"
  15 | ---
  16 | 
  17 | # PyTorch Issue Triage Skill
  18 | 
  19 | This skill helps triage GitHub issues by routing issues, applying labels, and leaving first-line responses.
  20 | 
  21 | ## Contents
  22 | - [MCP Tools Available](#mcp-tools-available)
  23 | - [Labels You Must NEVER Add](#labels-you-must-never-add)
  24 | - [Issue Triage Steps](#issue-triage-for-each-issue)
  25 |   - Step 0: Already Routed — SKIP
  26 |   - Step 1: Question vs Bug/Feature
  27 |   - Step 1.5: Needs Reproduction — External Files
  28 |   - Step 2: Transfer
  29 |   - Step 2.5: PT2 Issues — Special Handling
  30 |   - Step 3: Redirect to Secondary Oncall
  31 |   - Step 4: Label the Issue
  32 |   - Step 5: High Priority — REQUIRES HUMAN REVIEW
  33 |   - Step 6: bot-triaged (automatic)
  34 |   - Step 7: Mark Triaged
  35 | - [V1 Constraints](#v1-constraints)
  36 | 
  37 | **Labels reference:** See [labels.json](labels.json) for the full catalog of 305 labels suitable for triage. **ONLY apply labels that exist in this file.** Do not invent or guess label names. This file excludes CI triggers, test configs, release notes, and deprecated labels.
  38 | 
  39 | **PT2 triage guide:** See [pt2-triage-rubric.md](pt2-triage-rubric.md) for detailed labeling guidance when triaging PT2/torch.compile issues.
  40 | 
  41 | **Response templates:** See [templates.json](templates.json) for standard response messages.
  42 | 
  43 | ---
  44 | 
  45 | ## MCP Tools Available
  46 | 
  47 | Use these GitHub MCP tools for triage:
  48 | 
  49 | | Tool | Purpose |
  50 | |------|---------|
  51 | | `mcp__github__issue_read` | Get issue details, comments, and existing labels |
  52 | | `mcp__github__issue_write` | Apply labels or close issues |
  53 | | `mcp__github__add_issue_comment` | Add comment (only for redirecting questions) |
  54 | | `mcp__github__search_issues` | Find similar issues for context |
  55 | 
  56 | ---
  57 | 
  58 | ## Labels You Must NEVER Add
  59 | 
  60 | | Prefix/Category | Reason |
  61 | |-----------------|--------|
  62 | | Labels not in `labels.json` | Only apply labels that exist in the allowlist |
  63 | | `ciflow/*` | CI job triggers for PRs only |
  64 | | `test-config/*` | Test suite selectors for PRs only |
  65 | | `release notes: *` | Auto-assigned for release notes |
  66 | | `ci-*`, `ci:*` | CI infrastructure controls |
  67 | | `sev*` | Severity labels require human decision |
  68 | | `merge blocking` | Requires human decision |
  69 | | Any label containing "deprecated" | Obsolete |
  70 | | `oncall: releng` | Not a triage redirect target. Use `module: ci` instead |
  71 | 
  72 | **If blocked:** When a label is blocked by the hook, add ONLY `triage review` and stop. A human will handle it.
  73 | 
  74 | These rules are enforced by a PreToolUse hook that validates all labels against `labels.json`.
  75 | 
  76 | ### Never Override Human Labels
  77 | 
  78 | If a human has already applied labels (especially `ci: sev`, severity labels, or priority labels), do NOT remove or replace them. Your job is to supplement, not override.
  79 | 
  80 | ---
  81 | 
  82 | ## Issue Triage (for each issue)
  83 | 
  84 | ### 0) Already Routed — SKIP
  85 | 
  86 | **If an issue already has ANY `oncall:` label, SKIP IT entirely.** Do not:
  87 | - Add any labels
  88 | - Add `triaged`
  89 | - Leave comments
  90 | - Do any triage work
  91 | 
  92 | That issue belongs to the sub-oncall team. They own their queue.
  93 | 
  94 | ### 1) Question vs Bug/Feature
  95 | 
  96 | - If it is a question (not a bug report or feature request): close and use the `redirect_to_forum` template from `templates.json`.
  97 | - If unclear whether it is a bug/feature vs a question: request additional information using the `request_more_info` template and stop.
  98 | 
  99 | ### 1.5) Needs Reproduction — External Files
 100 | 
 101 | Check if the issue body contains links to external files that users would need to download to reproduce.
 102 | 
 103 | **Patterns to detect:**
 104 | - File attachments: `.zip`, `.pt`, `.pth`, `.pkl`, `.safetensors`, `.onnx`, `.bin` files
 105 | - External storage: Google Drive, Dropbox, OneDrive, Mega, WeTransfer links
 106 | - Model hubs: Hugging Face Hub links to model files
 107 | 
 108 | **Action:**
 109 | 1. **Edit the issue body** to remove/redact the download links
 110 |    - Replace with: `[Link removed - external file downloads are not permitted for security reasons]`
 111 | 2. Add `needs reproduction` label
 112 | 3. Use the `needs_reproduction` template from `templates.json` to request a self-contained reproduction
 113 | 4. Do NOT add `triaged` — wait for the user to provide a reproducible example
 114 | 
 115 | ### 1.55) Needs Reproduction — Other Cases
 116 | 
 117 | Also add `needs reproduction` when:
 118 | - The user reports a hardware-specific issue (e.g., specific GPU model) without a self-contained repro script
 119 | - The user references a specific model/checkpoint/dataset that is not publicly runnable in a few lines
 120 | - The issue describes version-upgrade breakage but only provides a high-level description without a minimal script
 121 | - The repro depends on a specific training setup, distributed environment, or non-trivial infrastructure
 122 | 
 123 | ### 1.6) Edge Cases & Numerical Accuracy
 124 | 
 125 | If the issue involves extremal values or numerical precision differences:
 126 | 
 127 | **Patterns to detect:**
 128 | - Values near `torch.finfo(dtype).max` or `torch.finfo(dtype).min`
 129 | - NaN/Inf appearing in outputs from valid (but extreme) inputs
 130 | - Differences between CPU and GPU results
 131 | - Precision differences between dtypes (e.g., fp32 vs fp16)
 132 | - Fuzzer-generated edge cases
 133 | 
 134 | **IMPORTANT — avoid keyword-triggered mislabeling:**
 135 | 
 136 | Label based on the **root cause**, not keywords that appear in the error or title. A keyword tells you what failed, not why.
 137 | 
 138 | - An `undefined symbol: ncclAlltoAll` error at `import torch` is a **packaging** issue (`module: binaries`), not a distributed training bug — the user never ran distributed code.
 139 | - A `nan` in a parameter name or tolerance check is not `module: NaNs and Infs` unless the bug is actually about NaN propagation.
 140 | - A stack trace mentioning `autograd` does not mean `module: autograd` — check whether the bug is in autograd itself or just on the call path.
 141 | - A test failure with tolerance thresholds is `module: tests`, not `module: numerical-stability`.
 142 | 
 143 | Ask: "Where would the fix need to be made?" That determines the label.
 144 | 
 145 | **Action:**
 146 | 1. Add `module: edge cases` label
 147 | 2. If from a fuzzer, also add `topic: fuzzer`
 148 | 3. Use the `numerical_accuracy` template from `templates.json` to link to the docs
 149 | 4. If the issue is clearly expected behavior per the docs, close it with the template comment
 150 | 
 151 | ### 2) Transfer (domain library or ExecuTorch)
 152 | 
 153 | If the issue belongs in another repo (vision/text/audio/RL/ExecuTorch/etc.), transfer the issue and **STOP**.
 154 | 
 155 | ### 2.5) PT2 Issues — Special Handling
 156 | 
 157 | **PT2 is NOT a redirect.** `oncall: pt2` is not like the other oncall labels in Step 3. PT2 issues continue through Steps 4–7 for full triage — add `oncall: pt2`, then proceed to label with `module:` labels, mark `triaged`, etc.
 158 | 
 159 | See [pt2-triage-rubric.md](pt2-triage-rubric.md) for detailed labeling decisions on which `module:` labels to apply.
 160 | 
 161 | ### 3) Redirect to Secondary Oncall
 162 | 
 163 | **CRITICAL:** When redirecting issues to a **non-PT2** oncall queue, apply exactly one `oncall: ...` label and **STOP**. Do NOT:
 164 | - Add any `module:` labels
 165 | - Mark it `triaged`
 166 | - Do any further triage work
 167 | 
 168 | The sub-oncall team will handle their own triage. Your job is only to route it to them.
 169 | 
 170 | #### Oncall Redirect Labels
 171 | 
 172 | | Label | When to use |
 173 | |-------|-------------|
 174 | | `oncall: jit` | TorchScript issues |
 175 | | `oncall: distributed` | Distributed training (DDP, FSDP, RPC, c10d, DTensor, DeviceMesh, symmetric memory, context parallel, pipelining) |
 176 | | `oncall: export` | torch.export issues |
 177 | | `oncall: quantization` | Quantization issues |
 178 | | `oncall: mobile` | Mobile (iOS/Android), excludes ExecuTorch |
 179 | | `oncall: profiler` | Profiler issues (CPU, GPU, Kineto) |
 180 | | `oncall: visualization` | TensorBoard integration |
 181 | 
 182 | **Common routing mistakes to avoid:**
 183 | - **MPS ≠ Mobile.** MPS (Metal Performance Shaders) is the macOS/Apple Silicon GPU backend. Do NOT route MPS issues to `oncall: mobile`. MPS issues stay in the general queue with `module: mps`.
 184 | - **DTensor → `oncall: distributed`.** DTensor issues should always be routed to `oncall: distributed`, even if they don't mention DDP/FSDP.
 185 | - **ONNX → `module: onnx`.** There is no `oncall: onnx`. Use `module: onnx` and keep in the general queue.
 186 | - **CI/releng → `module: ci`.** Do not use `oncall: releng`. Use `module: ci` for CI infrastructure issues.
 187 | - **torch.compile + distributed.** When `torch.compile` mishandles a distributed op (e.g., `dist.all_reduce`), the issue typically needs BOTH `oncall: pt2` and `oncall: distributed` since the fix may span both codebases.
 188 | 
 189 | **Note:** `oncall: cpu inductor` is a sub-queue of PT2. For general triage, just use `oncall: pt2`.
 190 | 
 191 | ### 4) Label the issue (if NOT transferred/redirected)
 192 | 
 193 | Only if the issue stays in the general queue:
 194 | - Add 1+ `module: ...` labels based on the affected area
 195 | - Prefer specific labels over general ones when both exist. Check `labels.json` descriptions for guidance on when a specific label supersedes a general one (e.g., `module: sdpa` instead of `module: nn` for SDPA issues, `module: flex attention` instead of `module: nn` for flex attention).
 196 | - `feature` — wholly new functionality that does not exist today in any form
 197 | - `enhancement` — improvement to something that already works (e.g., adding a native backend kernel for an op that already runs via fallback/composite, performance optimization, better error messages). If the enhancement is about performance, also add `module: performance`.
 198 | - `function request` — a new function or new arguments/modes for an existing function
 199 | - If the issue says the operation "currently works" or "falls back to" a slower path, that is `enhancement`, not `feature`
 200 | 
 201 | **Commonly missed labels — always check for these:**
 202 | 
 203 | | Condition | Label |
 204 | |-----------|-------|
 205 | | Segfault, illegal memory access, SIGSEGV | `module: crash` |
 206 | | Performance issue: regression, slowdown, or optimization request | `module: performance` |
 207 | | Issue on Windows | `module: windows` |
 208 | | Previously working feature now broken | `module: regression` |
 209 | | Broken docs/links that previously worked | `module: docs` + `module: regression` (NOT `enhancement`) |
 210 | | Issue about a test failing (not the underlying functionality) | `module: tests` |
 211 | | Backward pass / gradient computation bug | `module: autograd` (in addition to the op's module label) |
 212 | | `torch.linalg` ops or linear algebra ops (solve, svd, eig, inv, etc.) | `module: linear algebra` |
 213 | | `has workaround` | Only add when the workaround is **non-trivial and non-obvious**. If the issue is "X doesn't work for non-contiguous tensors," calling `.contiguous()` is the tautological inverse of the bug, not a workaround. A real workaround is something like installing a specific package version, adding a synchronization point, inserting `gc.collect()`, or using a different API that isn't obviously implied by the bug description. |
 214 | 
 215 | **Label based on the actual bug, not keywords.** Read the issue to understand what is actually broken. A bug about broadcasting that happens to mention "nan" in a parameter name is a frontend bug, not a NaN/Inf bug.
 216 | 
 217 | ### 5) High Priority — REQUIRES HUMAN REVIEW
 218 | 
 219 | **CRITICAL:** If you believe an issue is high priority, you MUST:
 220 | 1. Add `triage review` label and do not add `triaged`
 221 | 
 222 | Do NOT directly add `high priority` without human confirmation.
 223 | 
 224 | High priority criteria:
 225 | - Crash / segfault / illegal memory access
 226 | - Silent correctness issue (wrong results without error)
 227 | - Regression from a prior version
 228 | - Internal assert failure
 229 | - Many users affected
 230 | - Core component or popular model impact
 231 | 
 232 | ### 6) bot-triaged (automatic)
 233 | 
 234 | The `bot-triaged` label is automatically applied by a post-hook after any issue mutation. You do not need to add it manually.
 235 | 
 236 | ### 7) Mark triaged
 237 | 
 238 | If not transferred/redirected and not flagged for review, add `triaged`.
 239 | 
 240 | ---
 241 | 
 242 | ## V1 Constraints
 243 | 
 244 | **DO NOT:**
 245 | - Close bug reports or feature requests automatically
 246 | - Close issues unless they are clear usage questions per Step 1
 247 | - Assign issues to users
 248 | - Add `high priority` directly without human confirmation
 249 | - Add module labels when redirecting to oncall
 250 | - Add comments to bug reports or feature requests, except a single info request when classification is unclear
 251 | 
 252 | **DO:**
 253 | - Close clear usage questions and point to discuss.pytorch.org (per step 1)
 254 | - Be conservative - when in doubt, add `triage review` for human attention
 255 | - Apply type labels (`feature`, `enhancement`, `function request`) when confident
 256 | - Add `triaged` label when classification is complete
 257 | 
 258 | **Note:** `bot-triaged` is automatically applied by a post-hook after any issue mutation.
```


---
## .claude/skills/triaging-issues/labels.json

```
   1 | {
   2 |   "description": "Labels suitable for issue triage. Excludes CI triggers, test configs, release notes, deprecated, and PR-only labels.",
   3 |   "repo": "pytorch/pytorch",
   4 |   "count": 304,
   5 |   "labels": [
   6 |     {
   7 |       "name": "actionable",
   8 |       "description": "Clear what needs to be done to fix this issue"
   9 |     },
  10 |     {
  11 |       "name": "better-on-discuss-forum",
  12 |       "description": ""
  13 |     },
  14 |     {
  15 |       "name": "dynamo-autograd-function",
  16 |       "description": "Dynamo Autograd function (compile)"
  17 |     },
  18 |     {
  19 |       "name": "dynamo-functorch",
  20 |       "description": "Issues related to dynamo/compile on functorch transforms"
  21 |     },
  22 |     {
  23 |       "name": "enhancement",
  24 |       "description": "Improvement to something that already works: performance optimization, better error messages, adding a backend-native implementation for an op that already runs via fallback/composite"
  25 |     },
  26 |     {
  27 |       "name": "feature",
  28 |       "description": "A request for wholly new functionality that does not exist today in any form (no fallback, no composite, no workaround)"
  29 |     },
  30 |     {
  31 |       "name": "function request",
  32 |       "description": "A request for a new function or the addition of new arguments/modes to an existing function."
  33 |     },
  34 |     {
  35 |       "name": "fx",
  36 |       "description": ""
  37 |     },
  38 |     {
  39 |       "name": "good first issue",
  40 |       "description": "Good for new open source contributors"
  41 |     },
  42 |     {
  43 |       "name": "has workaround",
  44 |       "description": ""
  45 |     },
  46 |     {
  47 |       "name": "high priority",
  48 |       "description": "Crash, silent correctness, regression, or many users affected. Auto-adds triage review."
  49 |     },
  50 |     {
  51 |       "name": "inference mode",
  52 |       "description": "Everything related to InferenceMode guard"
  53 |     },
  54 |     {
  55 |       "name": "large",
  56 |       "description": "We think that this is a pretty chunky piece of work"
  57 |     },
  58 |     {
  59 |       "name": "llm-amenable",
  60 |       "description": ""
  61 |     },
  62 |     {
  63 |       "name": "low priority",
  64 |       "description": "We're unlikely to get around to doing this in the near future"
  65 |     },
  66 |     {
  67 |       "name": "matrix multiplication",
  68 |       "description": ""
  69 |     },
  70 |     {
  71 |       "name": "module: 64-bit",
  72 |       "description": "Problems related to incorrectly using 32-bit integers when 64-bit is needed (e.g., 8G tensors)"
  73 |     },
  74 |     {
  75 |       "name": "module: __torch_dispatch__",
  76 |       "description": ""
  77 |     },
  78 |     {
  79 |       "name": "module: __torch_function__",
  80 |       "description": ""
  81 |     },
  82 |     {
  83 |       "name": "module: abi",
  84 |       "description": "libtorch C++ ABI related problems"
  85 |     },
  86 |     {
  87 |       "name": "module: accelerator",
  88 |       "description": "Issues related to the shared accelerator API"
  89 |     },
  90 |     {
  91 |       "name": "module: activation checkpointing",
  92 |       "description": "Related to activation checkpointing"
  93 |     },
  94 |     {
  95 |       "name": "module: advanced indexing",
  96 |       "description": "Related to x[i] = y, index functions"
  97 |     },
  98 |     {
  99 |       "name": "module: amp (automated mixed precision)",
 100 |       "description": "autocast"
 101 |     },
 102 |     {
 103 |       "name": "module: android",
 104 |       "description": "Related to Android support"
 105 |     },
 106 |     {
 107 |       "name": "module: aotdispatch",
 108 |       "description": "umbrella label for AOTAutograd issues"
 109 |     },
 110 |     {
 111 |       "name": "module: aotinductor",
 112 |       "description": "aot inductor"
 113 |     },
 114 |     {
 115 |       "name": "module: arm",
 116 |       "description": "Related to ARM architectures builds of PyTorch. Includes Apple M1"
 117 |     },
 118 |     {
 119 |       "name": "module: autograd",
 120 |       "description": "Related to torch.autograd, and the autograd engine in general"
 121 |     },
 122 |     {
 123 |       "name": "module: backend",
 124 |       "description": "non-standard backend support"
 125 |     },
 126 |     {
 127 |       "name": "module: batching",
 128 |       "description": ""
 129 |     },
 130 |     {
 131 |       "name": "module: bc-breaking",
 132 |       "description": "Related to a BC-breaking change"
 133 |     },
 134 |     {
 135 |       "name": "module: benchmark",
 136 |       "description": "related to torch.utils.benchmark e.g. Timer"
 137 |     },
 138 |     {
 139 |       "name": "module: bfloat16",
 140 |       "description": ""
 141 |     },
 142 |     {
 143 |       "name": "module: binaries",
 144 |       "description": "Packaging, wheel, and install issues: undefined symbols at import time, version mismatches between pip-installed packages, missing shared libraries (libtorch_cuda.so, libnccl, libcudnn), and broken official binaries"
 145 |     },
 146 |     {
 147 |       "name": "module: bottleneck",
 148 |       "description": "Related to torch.utils.bottleneck"
 149 |     },
 150 |     {
 151 |       "name": "module: build",
 152 |       "description": "Build system issues, compilation errors, including bazel build failures"
 153 |     },
 154 |     {
 155 |       "name": "module: build warnings",
 156 |       "description": "Related to warnings during build process"
 157 |     },
 158 |     {
 159 |       "name": "module: ci",
 160 |       "description": "Related to continuous integration"
 161 |     },
 162 |     {
 163 |       "name": "module: codegen",
 164 |       "description": "Issues related to the codegen for Aten and Autograd"
 165 |     },
 166 |     {
 167 |       "name": "module: collect_env.py",
 168 |       "description": "Related to collect_env.py, which collects system information about users"
 169 |     },
 170 |     {
 171 |       "name": "module: compile ux",
 172 |       "description": "UX issues related to torch.compile"
 173 |     },
 174 |     {
 175 |       "name": "module: compile-time",
 176 |       "description": "Compilation mechanism or time spent in (re)compilation, tracing, startup"
 177 |     },
 178 |     {
 179 |       "name": "module: compiled autograd",
 180 |       "description": "compiled_autograd"
 181 |     },
 182 |     {
 183 |       "name": "module: complex",
 184 |       "description": "Related to complex number support in PyTorch"
 185 |     },
 186 |     {
 187 |       "name": "module: context parallel",
 188 |       "description": "PyTorch Context Parallel"
 189 |     },
 190 |     {
 191 |       "name": "module: convolution",
 192 |       "description": "Problems related to convolutions (THNN, THCUNN, CuDNN)"
 193 |     },
 194 |     {
 195 |       "name": "module: copy on write",
 196 |       "description": "Related to copy on write"
 197 |     },
 198 |     {
 199 |       "name": "module: core aten",
 200 |       "description": "Related to change to the Core ATen opset"
 201 |     },
 202 |     {
 203 |       "name": "module: correctness (silent)",
 204 |       "description": "issue that returns an incorrect result silently"
 205 |     },
 206 |     {
 207 |       "name": "module: cpp",
 208 |       "description": "Related to C++ API"
 209 |     },
 210 |     {
 211 |       "name": "module: cpp-extensions",
 212 |       "description": "Related to torch.utils.cpp_extension"
 213 |     },
 214 |     {
 215 |       "name": "module: cpu",
 216 |       "description": "CPU specific problem (e.g., perf, algorithm)"
 217 |     },
 218 |     {
 219 |       "name": "module: crash",
 220 |       "description": "Problem manifests as a hard crash, as opposed to a RuntimeError"
 221 |     },
 222 |     {
 223 |       "name": "module: cublas",
 224 |       "description": "Problem related to cublas support"
 225 |     },
 226 |     {
 227 |       "name": "module: cuda",
 228 |       "description": "Related to torch.cuda, and CUDA support in general"
 229 |     },
 230 |     {
 231 |       "name": "module: cuda graphs",
 232 |       "description": "Ability to capture and then replay streams of CUDA kernels"
 233 |     },
 234 |     {
 235 |       "name": "module: CUDACachingAllocator",
 236 |       "description": ""
 237 |     },
 238 |     {
 239 |       "name": "module: cudnn",
 240 |       "description": "Related to torch.backends.cudnn, and CuDNN support"
 241 |     },
 242 |     {
 243 |       "name": "module: custom-operators",
 244 |       "description": "custom operators, custom ops, custom-operators, custom-ops"
 245 |     },
 246 |     {
 247 |       "name": "module: data",
 248 |       "description": "torch.utils.data"
 249 |     },
 250 |     {
 251 |       "name": "module: data parallel",
 252 |       "description": ""
 253 |     },
 254 |     {
 255 |       "name": "module: dataloader",
 256 |       "description": "Related to torch.utils.data.DataLoader and Sampler"
 257 |     },
 258 |     {
 259 |       "name": "module: ddp",
 260 |       "description": "Issues/PRs related distributed data parallel training"
 261 |     },
 262 |     {
 263 |       "name": "module: deadlock",
 264 |       "description": "Problems related to deadlocks (hang without exiting)"
 265 |     },
 266 |     {
 267 |       "name": "module: debug-build",
 268 |       "description": "Related to building and testing PyTorch in debug mode"
 269 |     },
 270 |     {
 271 |       "name": "module: decompositions",
 272 |       "description": "Topics related to decomposition (excluding PrimTorch)"
 273 |     },
 274 |     {
 275 |       "name": "module: dependency bug",
 276 |       "description": "Problem is not caused by us, but caused by an upstream library we use"
 277 |     },
 278 |     {
 279 |       "name": "module: deploy",
 280 |       "description": "related to torch deploy torchdeploy"
 281 |     },
 282 |     {
 283 |       "name": "module: deprecation",
 284 |       "description": ""
 285 |     },
 286 |     {
 287 |       "name": "module: derivatives",
 288 |       "description": "Related to derivatives of operators"
 289 |     },
 290 |     {
 291 |       "name": "module: determinism",
 292 |       "description": "Issues related to torch.use_deterministic_algorithms(), deterministic mode, and reproducibility of results"
 293 |     },
 294 |     {
 295 |       "name": "module: DeviceMesh",
 296 |       "description": ""
 297 |     },
 298 |     {
 299 |       "name": "module: devx",
 300 |       "description": "Related to PyTorch contribution experience (HUD, pytorchbot)"
 301 |     },
 302 |     {
 303 |       "name": "module: dispatch",
 304 |       "description": "DispatchStub, Type, void pointer table, c10 dispatch"
 305 |     },
 306 |     {
 307 |       "name": "module: distance functions",
 308 |       "description": ""
 309 |     },
 310 |     {
 311 |       "name": "module: distributed_tool",
 312 |       "description": "tools to help distributed training"
 313 |     },
 314 |     {
 315 |       "name": "module: distributions",
 316 |       "description": "Related to torch.distributions"
 317 |     },
 318 |     {
 319 |       "name": "module: dlpack",
 320 |       "description": ""
 321 |     },
 322 |     {
 323 |       "name": "module: doc infra",
 324 |       "description": "Related to pytorch.org/docs, deployment of, and serving"
 325 |     },
 326 |     {
 327 |       "name": "module: docker",
 328 |       "description": ""
 329 |     },
 330 |     {
 331 |       "name": "module: docs",
 332 |       "description": "Related to our documentation, both in docs/ and docblocks"
 333 |     },
 334 |     {
 335 |       "name": "module: double backwards",
 336 |       "description": "Problem is related to double backwards definition on an operator"
 337 |     },
 338 |     {
 339 |       "name": "module: dtensor",
 340 |       "description": "distributed tensor tag"
 341 |     },
 342 |     {
 343 |       "name": "module: dynamic shapes",
 344 |       "description": "Related to symbolic/dynamic shapes in torch.compile"
 345 |     },
 346 |     {
 347 |       "name": "module: dynamo",
 348 |       "description": "Related to TorchDynamo (torch.compile frontend/tracing)"
 349 |     },
 350 |     {
 351 |       "name": "module: edge cases",
 352 |       "description": "Adversarial inputs unlikely to occur in practice. Add when inputs are at dtype limits (torch.finfo.max/min), extreme tensor shapes, or unusual values that stress numerical limits."
 353 |     },
 354 |     {
 355 |       "name": "module: elastic",
 356 |       "description": "Related to torch.distributed.elastic"
 357 |     },
 358 |     {
 359 |       "name": "module: embedding",
 360 |       "description": ""
 361 |     },
 362 |     {
 363 |       "name": "module: empty tensor",
 364 |       "description": ""
 365 |     },
 366 |     {
 367 |       "name": "module: error checking",
 368 |       "description": "Bugs related to incorrect/lacking error checking"
 369 |     },
 370 |     {
 371 |       "name": "module: expecttest",
 372 |       "description": "Expect test related functionality"
 373 |     },
 374 |     {
 375 |       "name": "module: fakeTensor",
 376 |       "description": ""
 377 |     },
 378 |     {
 379 |       "name": "module: fft",
 380 |       "description": ""
 381 |     },
 382 |     {
 383 |       "name": "module: first class dims",
 384 |       "description": ""
 385 |     },
 386 |     {
 387 |       "name": "module: flex attention",
 388 |       "description": "torch.nn.attention.flex_attention API. Use instead of module: nn for flex attention issues"
 389 |     },
 390 |     {
 391 |       "name": "module: floatx (formerly float8)",
 392 |       "description": "For torch.float8_e5m2 and torch.float8_e4m3 and other sub 8-bit float types"
 393 |     },
 394 |     {
 395 |       "name": "module: flop counter",
 396 |       "description": "FlopCounterMode mode"
 397 |     },
 398 |     {
 399 |       "name": "module: forward ad",
 400 |       "description": ""
 401 |     },
 402 |     {
 403 |       "name": "module: fsdp",
 404 |       "description": ""
 405 |     },
 406 |     {
 407 |       "name": "module: functional UX",
 408 |       "description": ""
 409 |     },
 410 |     {
 411 |       "name": "module: functionalization",
 412 |       "description": "used for issues that are specific to functionalization (AOTAutograd bugs should start w aotdispatch)"
 413 |     },
 414 |     {
 415 |       "name": "module: functorch",
 416 |       "description": "Pertaining to torch.func or pytorch/functorch"
 417 |     },
 418 |     {
 419 |       "name": "module: fx",
 420 |       "description": ""
 421 |     },
 422 |     {
 423 |       "name": "module: fx.passes",
 424 |       "description": "Optimization passes written in FX (don't forget to select a more specific label)"
 425 |     },
 426 |     {
 427 |       "name": "module: graph breaks",
 428 |       "description": ""
 429 |     },
 430 |     {
 431 |       "name": "module: guards",
 432 |       "description": ""
 433 |     },
 434 |     {
 435 |       "name": "module: half",
 436 |       "description": "Related to float16 half-precision floats"
 437 |     },
 438 |     {
 439 |       "name": "module: helion",
 440 |       "description": ""
 441 |     },
 442 |     {
 443 |       "name": "module: higher order operators",
 444 |       "description": "torch.cond and similar"
 445 |     },
 446 |     {
 447 |       "name": "module: hpu",
 448 |       "description": "Issues related to the hpu device (Habana/Gaudi)"
 449 |     },
 450 |     {
 451 |       "name": "module: hub",
 452 |       "description": ""
 453 |     },
 454 |     {
 455 |       "name": "module: inductor",
 456 |       "description": "Related to TorchInductor (torch.compile codegen backend)"
 457 |     },
 458 |     {
 459 |       "name": "module: infallible views",
 460 |       "description": ""
 461 |     },
 462 |     {
 463 |       "name": "module: infra",
 464 |       "description": "Relates to CI infrastructure"
 465 |     },
 466 |     {
 467 |       "name": "module: initialization",
 468 |       "description": "Related to weight initialization on operators"
 469 |     },
 470 |     {
 471 |       "name": "module: int overflow",
 472 |       "description": ""
 473 |     },
 474 |     {
 475 |       "name": "module: intel",
 476 |       "description": "Specific to x86 architecture"
 477 |     },
 478 |     {
 479 |       "name": "module: internals",
 480 |       "description": "Related to internal abstractions in c10 and ATen"
 481 |     },
 482 |     {
 483 |       "name": "module: interpolation",
 484 |       "description": ""
 485 |     },
 486 |     {
 487 |       "name": "module: ios",
 488 |       "description": "Related to iOS support - build, API, Continuous Integration, document"
 489 |     },
 490 |     {
 491 |       "name": "module: jetson",
 492 |       "description": "Related to the Jetson builds by NVIDIA"
 493 |     },
 494 |     {
 495 |       "name": "module: jiterator",
 496 |       "description": ""
 497 |     },
 498 |     {
 499 |       "name": "module: known issue",
 500 |       "description": ""
 501 |     },
 502 |     {
 503 |       "name": "module: language binding",
 504 |       "description": "support for language bindings, including languages that aren't currently supported"
 505 |     },
 506 |     {
 507 |       "name": "module: lazy",
 508 |       "description": ""
 509 |     },
 510 |     {
 511 |       "name": "module: library",
 512 |       "description": "Related to torch.library (for registering ops from Python)"
 513 |     },
 514 |     {
 515 |       "name": "module: linear algebra",
 516 |       "description": "Issues related to specialized linear algebra operations in PyTorch; includes matrix multiply matmul"
 517 |     },
 518 |     {
 519 |       "name": "module: lint",
 520 |       "description": "Issues related to our Python/C++ lint rules (run by Travis)"
 521 |     },
 522 |     {
 523 |       "name": "module: log classifier",
 524 |       "description": "Issues related to CI log classification improvements"
 525 |     },
 526 |     {
 527 |       "name": "module: logging",
 528 |       "description": "Features which make it easier to tell what PyTorch is doing under the hood"
 529 |     },
 530 |     {
 531 |       "name": "module: loss",
 532 |       "description": "Problem is related to loss function"
 533 |     },
 534 |     {
 535 |       "name": "module: LrScheduler",
 536 |       "description": ""
 537 |     },
 538 |     {
 539 |       "name": "module: lts",
 540 |       "description": "related to Enterprise PyTorch"
 541 |     },
 542 |     {
 543 |       "name": "module: m1",
 544 |       "description": ""
 545 |     },
 546 |     {
 547 |       "name": "module: macos",
 548 |       "description": "Mac OS related issues"
 549 |     },
 550 |     {
 551 |       "name": "module: magma",
 552 |       "description": "related to magma linear algebra cuda support"
 553 |     },
 554 |     {
 555 |       "name": "module: masked operators",
 556 |       "description": "Masked operations"
 557 |     },
 558 |     {
 559 |       "name": "module: memory format",
 560 |       "description": "Memory format/layout related issues/changes (channels_last, nhwc)"
 561 |     },
 562 |     {
 563 |       "name": "module: memory usage",
 564 |       "description": "PyTorch is using more memory than it should, or it is leaking memory"
 565 |     },
 566 |     {
 567 |       "name": "module: meta tensors",
 568 |       "description": ""
 569 |     },
 570 |     {
 571 |       "name": "module: minifier",
 572 |       "description": ""
 573 |     },
 574 |     {
 575 |       "name": "module: mkl",
 576 |       "description": "Related to our MKL support"
 577 |     },
 578 |     {
 579 |       "name": "module: mkldnn",
 580 |       "description": "Related to Intel IDEEP or oneDNN (a.k.a. mkldnn) integration"
 581 |     },
 582 |     {
 583 |       "name": "module: models",
 584 |       "description": ""
 585 |     },
 586 |     {
 587 |       "name": "module: molly-guard",
 588 |       "description": "Features which help prevent users from committing common mistakes"
 589 |     },
 590 |     {
 591 |       "name": "module: mpi",
 592 |       "description": "Problems related to MPI support"
 593 |     },
 594 |     {
 595 |       "name": "module: mps",
 596 |       "description": "Related to Apple Metal Performance Shaders framework"
 597 |     },
 598 |     {
 599 |       "name": "module: mta",
 600 |       "description": "Issues related to multi-tensor apply kernels and foreach functions"
 601 |     },
 602 |     {
 603 |       "name": "module: mtia",
 604 |       "description": "Device MTIA related issues"
 605 |     },
 606 |     {
 607 |       "name": "module: multi-gpu",
 608 |       "description": "Problem is related to running on multiple GPUs"
 609 |     },
 610 |     {
 611 |       "name": "module: multiprocessing",
 612 |       "description": "Related to torch.multiprocessing"
 613 |     },
 614 |     {
 615 |       "name": "module: multithreading",
 616 |       "description": "Related to issues that occur when running on multiple CPU threads"
 617 |     },
 618 |     {
 619 |       "name": "module: named tensor",
 620 |       "description": "Named tensor support"
 621 |     },
 622 |     {
 623 |       "name": "module: NaNs and Infs",
 624 |       "description": "Problems related to NaN and Inf handling in floating point"
 625 |     },
 626 |     {
 627 |       "name": "module: nativert",
 628 |       "description": "Everything related to the ExecuTorch full runtime that lives in libtorch"
 629 |     },
 630 |     {
 631 |       "name": "module: nccl",
 632 |       "description": "Problems related to nccl support"
 633 |     },
 634 |     {
 635 |       "name": "module: nestedtensor",
 636 |       "description": "NestedTensor tag see issue #25032"
 637 |     },
 638 |     {
 639 |       "name": "module: nn",
 640 |       "description": "Related to torch.nn"
 641 |     },
 642 |     {
 643 |       "name": "module: nn.utils.parametrize",
 644 |       "description": ""
 645 |     },
 646 |     {
 647 |       "name": "module: nnpack",
 648 |       "description": "Related to our NNPack integration"
 649 |     },
 650 |     {
 651 |       "name": "module: norms and normalization",
 652 |       "description": ""
 653 |     },
 654 |     {
 655 |       "name": "module: numba",
 656 |       "description": ""
 657 |     },
 658 |     {
 659 |       "name": "module: numerical-reproducibility",
 660 |       "description": ""
 661 |     },
 662 |     {
 663 |       "name": "module: numerical-stability",
 664 |       "description": "Problems related to numerical stability of operations"
 665 |     },
 666 |     {
 667 |       "name": "module: numpy",
 668 |       "description": "Related to numpy support, and also numpy compatibility of our operators"
 669 |     },
 670 |     {
 671 |       "name": "module: nvfuser",
 672 |       "description": ""
 673 |     },
 674 |     {
 675 |       "name": "module: onnx",
 676 |       "description": "Related to torch.onnx"
 677 |     },
 678 |     {
 679 |       "name": "module: op-unification",
 680 |       "description": "Problem would be solved if we unified Caffe2 and PyTorch implementations of an operator"
 681 |     },
 682 |     {
 683 |       "name": "module: opcheck",
 684 |       "description": "Related to opcheck testing for custom operators"
 685 |     },
 686 |     {
 687 |       "name": "module: openblas",
 688 |       "description": ""
 689 |     },
 690 |     {
 691 |       "name": "module: openmp",
 692 |       "description": "Related to OpenMP (omp) support in PyTorch"
 693 |     },
 694 |     {
 695 |       "name": "module: openreg",
 696 |       "description": ""
 697 |     },
 698 |     {
 699 |       "name": "module: optimizer",
 700 |       "description": "Related to torch.optim"
 701 |     },
 702 |     {
 703 |       "name": "module: padding",
 704 |       "description": ""
 705 |     },
 706 |     {
 707 |       "name": "module: pallas",
 708 |       "description": "Pallas backend related issues"
 709 |     },
 710 |     {
 711 |       "name": "module: partial aliasing",
 712 |       "description": "Related to correctly supporting overlapping storages in operations"
 713 |     },
 714 |     {
 715 |       "name": "module: performance",
 716 |       "description": "Issues related to performance, either of kernel code or framework glue"
 717 |     },
 718 |     {
 719 |       "name": "module: pickle",
 720 |       "description": "Problems related to pickling of PyTorch objects"
 721 |     },
 722 |     {
 723 |       "name": "module: pipelining",
 724 |       "description": "Pipeline Parallelism"
 725 |     },
 726 |     {
 727 |       "name": "module: pooling",
 728 |       "description": ""
 729 |     },
 730 |     {
 731 |       "name": "module: porting",
 732 |       "description": "Issues related to porting TH/THNN legacy to ATen native"
 733 |     },
 734 |     {
 735 |       "name": "module: POWER",
 736 |       "description": "Issues specific to the POWER/ppc architecture"
 737 |     },
 738 |     {
 739 |       "name": "module: primTorch",
 740 |       "description": ""
 741 |     },
 742 |     {
 743 |       "name": "module: printing",
 744 |       "description": "Issues related to the printing format of tensors"
 745 |     },
 746 |     {
 747 |       "name": "module: PrivateUse1",
 748 |       "description": "private use"
 749 |     },
 750 |     {
 751 |       "name": "module: protobuf",
 752 |       "description": ""
 753 |     },
 754 |     {
 755 |       "name": "module: ProxyTensor",
 756 |       "description": "make_fx and related"
 757 |     },
 758 |     {
 759 |       "name": "module: pruning",
 760 |       "description": ""
 761 |     },
 762 |     {
 763 |       "name": "module: pt2 accuracy",
 764 |       "description": ""
 765 |     },
 766 |     {
 767 |       "name": "module: pt2 optimizer",
 768 |       "description": "Relating to torch.compile'd optim"
 769 |     },
 770 |     {
 771 |       "name": "module: pt2-dispatcher",
 772 |       "description": "PT2  dispatcher-related issues (e.g., aotdispatch, functionalization, faketensor, custom-op,"
 773 |     },
 774 |     {
 775 |       "name": "module: pybind",
 776 |       "description": "Related to our Python bindings / interactions with other Python libraries"
 777 |     },
 778 |     {
 779 |       "name": "module: python array api",
 780 |       "description": "Issues related to the Python Array API"
 781 |     },
 782 |     {
 783 |       "name": "module: python dispatcher",
 784 |       "description": ""
 785 |     },
 786 |     {
 787 |       "name": "module: python frontend",
 788 |       "description": "For issues relating to PyTorch's Python frontend"
 789 |     },
 790 |     {
 791 |       "name": "module: python version",
 792 |       "description": "Issues related to specific Python versions"
 793 |     },
 794 |     {
 795 |       "name": "module: pytree",
 796 |       "description": ""
 797 |     },
 798 |     {
 799 |       "name": "module: random",
 800 |       "description": "Related to random number generation in PyTorch (rng generator)"
 801 |     },
 802 |     {
 803 |       "name": "module: reductions",
 804 |       "description": ""
 805 |     },
 806 |     {
 807 |       "name": "module: regression",
 808 |       "description": "It used to work, and now it doesn't"
 809 |     },
 810 |     {
 811 |       "name": "module: reinplacing",
 812 |       "description": "inductor reinplacing, re-inplacing, auto-functionalization, auto functionalization, custom op"
 813 |     },
 814 |     {
 815 |       "name": "module: risc-v",
 816 |       "description": "All issues related to RISC-V architecture"
 817 |     },
 818 |     {
 819 |       "name": "module: rnn",
 820 |       "description": "Issues related to RNN support (LSTM, GRU, etc)"
 821 |     },
 822 |     {
 823 |       "name": "module: rocm",
 824 |       "description": "AMD GPU support for Pytorch"
 825 |     },
 826 |     {
 827 |       "name": "module: rpc",
 828 |       "description": "Related to RPC, distributed autograd, RRef, and distributed optimizer"
 829 |     },
 830 |     {
 831 |       "name": "module: safe resize",
 832 |       "description": ""
 833 |     },
 834 |     {
 835 |       "name": "module: sanitizers",
 836 |       "description": ""
 837 |     },
 838 |     {
 839 |       "name": "module: scatter & gather ops",
 840 |       "description": ""
 841 |     },
 842 |     {
 843 |       "name": "module: scientific computing",
 844 |       "description": ""
 845 |     },
 846 |     {
 847 |       "name": "module: scipy compatibility",
 848 |       "description": ""
 849 |     },
 850 |     {
 851 |       "name": "module: sdpa",
 852 |       "description": "scaled_dot_product_attention and its backends (math, flash, mem_efficient, cudnn). Use instead of module: nn for SDPA issues"
 853 |     },
 854 |     {
 855 |       "name": "module: selective build",
 856 |       "description": ""
 857 |     },
 858 |     {
 859 |       "name": "module: serialization",
 860 |       "description": "Issues related to serialization (e.g., via pickle, or otherwise) of PyTorch objects"
 861 |     },
 862 |     {
 863 |       "name": "module: shape checking",
 864 |       "description": ""
 865 |     },
 866 |     {
 867 |       "name": "module: single threaded",
 868 |       "description": "Related to single-threaded execution"
 869 |     },
 870 |     {
 871 |       "name": "module: sleef",
 872 |       "description": "Problems related to SLEEF support"
 873 |     },
 874 |     {
 875 |       "name": "module: sorting and selection",
 876 |       "description": ""
 877 |     },
 878 |     {
 879 |       "name": "module: sparse",
 880 |       "description": "Related to torch.sparse"
 881 |     },
 882 |     {
 883 |       "name": "module: special",
 884 |       "description": "Functions with no exact solutions, analogous to those in scipy.special"
 885 |     },
 886 |     {
 887 |       "name": "module: static linking",
 888 |       "description": "Related to statically linked libtorch (we dynamically link by default)"
 889 |     },
 890 |     {
 891 |       "name": "module: structured kernels",
 892 |       "description": "Related to new structured kernels functionality"
 893 |     },
 894 |     {
 895 |       "name": "module: symm_mem",
 896 |       "description": "Issues and PRs of Symmetric Memory"
 897 |     },
 898 |     {
 899 |       "name": "module: tbb",
 900 |       "description": ""
 901 |     },
 902 |     {
 903 |       "name": "module: tensor creation",
 904 |       "description": ""
 905 |     },
 906 |     {
 907 |       "name": "module: tensorboard",
 908 |       "description": ""
 909 |     },
 910 |     {
 911 |       "name": "module: tensorflow",
 912 |       "description": ""
 913 |     },
 914 |     {
 915 |       "name": "module: TensorIterator",
 916 |       "description": ""
 917 |     },
 918 |     {
 919 |       "name": "module: tensorpipe",
 920 |       "description": "Related to Tensorpipe RPC Agent"
 921 |     },
 922 |     {
 923 |       "name": "module: testing",
 924 |       "description": "Issues related to the torch.testing module (not tests)"
 925 |     },
 926 |     {
 927 |       "name": "module: tests",
 928 |       "description": "Issues related to tests (not the torch.testing module)"
 929 |     },
 930 |     {
 931 |       "name": "module: tf32",
 932 |       "description": "Related to tf32 data format"
 933 |     },
 934 |     {
 935 |       "name": "module: third_party",
 936 |       "description": ""
 937 |     },
 938 |     {
 939 |       "name": "module: threaded pg",
 940 |       "description": "MultiThreaded ProcessGroup aka ProcessLocalGroup"
 941 |     },
 942 |     {
 943 |       "name": "module: torchbind",
 944 |       "description": ""
 945 |     },
 946 |     {
 947 |       "name": "module: trace",
 948 |       "description": "Related to structured logging under TORCH_TRACE trace_structured"
 949 |     },
 950 |     {
 951 |       "name": "module: trigonometric functions",
 952 |       "description": ""
 953 |     },
 954 |     {
 955 |       "name": "module: type promotion",
 956 |       "description": "Related to semantics of type promotion"
 957 |     },
 958 |     {
 959 |       "name": "module: typing",
 960 |       "description": "Related to mypy type annotations"
 961 |     },
 962 |     {
 963 |       "name": "module: undefined reference",
 964 |       "description": "Build issues that manifest as \"undefined reference\""
 965 |     },
 966 |     {
 967 |       "name": "module: unknown",
 968 |       "description": "We do not know who is responsible for this feature, bug, or test case."
 969 |     },
 970 |     {
 971 |       "name": "module: unsigned int",
 972 |       "description": "Related to the new uint16, uint32, uint64 types"
 973 |     },
 974 |     {
 975 |       "name": "module: user triton",
 976 |       "description": "related to ability to directly torch.compile triton kernels"
 977 |     },
 978 |     {
 979 |       "name": "module: ux",
 980 |       "description": ""
 981 |     },
 982 |     {
 983 |       "name": "module: vectorization",
 984 |       "description": "Related to SIMD vectorization, e.g., Vec256"
 985 |     },
 986 |     {
 987 |       "name": "module: viewing and reshaping",
 988 |       "description": ""
 989 |     },
 990 |     {
 991 |       "name": "module: vision",
 992 |       "description": ""
 993 |     },
 994 |     {
 995 |       "name": "module: vllm",
 996 |       "description": ""
 997 |     },
 998 |     {
 999 |       "name": "module: vmap",
1000 |       "description": ""
1001 |     },
1002 |     {
1003 |       "name": "module: vulkan",
1004 |       "description": ""
1005 |     },
1006 |     {
1007 |       "name": "module: windows",
1008 |       "description": "Windows support for PyTorch"
1009 |     },
1010 |     {
1011 |       "name": "module: wsl",
1012 |       "description": "Related to Windows Subsystem for Linux"
1013 |     },
1014 |     {
1015 |       "name": "module: xla",
1016 |       "description": "Related to XLA support"
1017 |     },
1018 |     {
1019 |       "name": "module: xnnpack",
1020 |       "description": ""
1021 |     },
1022 |     {
1023 |       "name": "module: xpu",
1024 |       "description": "Intel XPU related issues"
1025 |     },
1026 |     {
1027 |       "name": "needs design",
1028 |       "description": "We want to add this feature but we need to figure out how first"
1029 |     },
1030 |     {
1031 |       "name": "needs reproduction",
1032 |       "description": "Ensure you have actionable steps to reproduce the issue. Someone else needs to confirm the repro. Add when issue requires downloading external files (.zip, .pt, .pth, .pkl, .safetensors) or links to external storage (Google Drive, Dropbox) to reproduce."
1033 |     },
1034 |     {
1035 |       "name": "needs research",
1036 |       "description": "We need to decide whether or not this merits inclusion, based on research world"
1037 |     },
1038 |     {
1039 |       "name": "newcomer",
1040 |       "description": ""
1041 |     },
1042 |     {
1043 |       "name": "oncall: cpu inductor",
1044 |       "description": "CPU Inductor issues for Intel team to triage"
1045 |     },
1046 |     {
1047 |       "name": "oncall: distributed",
1048 |       "description": "Add this issue/PR to distributed oncall triage queue"
1049 |     },
1050 |     {
1051 |       "name": "oncall: distributed checkpointing",
1052 |       "description": "Oncall label should be attached to any issues related to distributed checkpointing."
1053 |     },
1054 |     {
1055 |       "name": "oncall: export",
1056 |       "description": "Add this issue/PR to Export oncall triage queue"
1057 |     },
1058 |     {
1059 |       "name": "oncall: jit",
1060 |       "description": "Add this issue/PR to JIT oncall triage queue"
1061 |     },
1062 |     {
1063 |       "name": "oncall: mobile",
1064 |       "description": "Related to mobile support, including iOS and Android"
1065 |     },
1066 |     {
1067 |       "name": "oncall: package/deploy",
1068 |       "description": "Add issue/PR to torch.package TODO board"
1069 |     },
1070 |     {
1071 |       "name": "oncall: profiler",
1072 |       "description": "profiler-related issues (cpu, gpu, kineto)"
1073 |     },
1074 |     {
1075 |       "name": "oncall: pt2",
1076 |       "description": "Add this issue/PR to PT2 (torch.compile/dynamo/inductor) oncall triage queue"
1077 |     },
1078 |     {
1079 |       "name": "oncall: quantization",
1080 |       "description": "Quantization support in PyTorch"
1081 |     },
1082 |     {
1083 |       "name": "oncall: r2p",
1084 |       "description": "Add this issue/PR to R2P (elastic) oncall triage queue"
1085 |     },
1086 |     {
1087 |       "name": "oncall: releng",
1088 |       "description": "In support of CI and Release Engineering"
1089 |     },
1090 |     {
1091 |       "name": "oncall: speech_infra",
1092 |       "description": "Speech Infra oncall"
1093 |     },
1094 |     {
1095 |       "name": "oncall: visualization",
1096 |       "description": "Related to visualization in PyTorch, e.g., tensorboard"
1097 |     },
1098 |     {
1099 |       "name": "op-bench",
1100 |       "description": "PyTorch/Caffe2 Operator Micro-benchmarks"
1101 |     },
1102 |     {
1103 |       "name": "OSS contribution wanted",
1104 |       "description": "PR from open source contributors welcome to solve this issue."
1105 |     },
1106 |     {
1107 |       "name": "pipeline parallelism",
1108 |       "description": "Issues related to https://pytorch.org/docs/master/pipeline.html"
1109 |     },
1110 |     {
1111 |       "name": "proposal accepted",
1112 |       "description": "The core team has reviewed the feature request and agreed it would be a useful addition to PyTorch"
1113 |     },
1114 |     {
1115 |       "name": "release-feature-request",
1116 |       "description": "This tag is to mark Feature Tracked for PyTorch OSS Releases"
1117 |     },
1118 |     {
1119 |       "name": "security",
1120 |       "description": ""
1121 |     },
1122 |     {
1123 |       "name": "skipped",
1124 |       "description": "Denotes a (flaky) test currently skipped in CI."
1125 |     },
1126 |     {
1127 |       "name": "small",
1128 |       "description": "We think this is a small issue to fix. Consider knocking off high priority small issues"
1129 |     },
1130 |     {
1131 |       "name": "tensor subclass",
1132 |       "description": "Related to tensor subclasses"
1133 |     },
1134 |     {
1135 |       "name": "topic: fuzzer",
1136 |       "description": ""
1137 |     },
1138 |     {
1139 |       "name": "triage review",
1140 |       "description": "Needs discussion at weekly triage meeting"
1141 |     },
1142 |     {
1143 |       "name": "triaged",
1144 |       "description": "This issue has been looked at a team member, and triaged and prioritized into an appropriate module"
1145 |     },
1146 |     {
1147 |       "name": "upstream triton",
1148 |       "description": "Upstream Triton Issue"
1149 |     }
1150 |   ]
1151 | }
```


---
## .claude/skills/triaging-issues/pt2-triage-rubric.md

```
   1 | # PT2 Triage Rubric
   2 | 
   3 | This rubric guides labeling decisions for PT2 oncall triage.
   4 | 
   5 | ## 1. Component Isolation - Be Precise, Don't Over-Tag
   6 | 
   7 | ### Dynamo vs Dynamic Shapes
   8 | 
   9 | | Signal | Label |
  10 | |--------|-------|
  11 | | `dynamic=False` fixes it | `module: dynamic shapes` only |
  12 | | Graph breaks, bytecode errors | `module: dynamo` |
  13 | | Guard failures, SymInt issues | `module: dynamic shapes` |
  14 | | Data-dependent operations (.item(), etc.) | `module: dynamic shapes` |
  15 | 
  16 | **Don't just slap `module: dynamo` on every torch.compile issue.**
  17 | 
  18 | ---
  19 | 
  20 | ## 2. Backend Isolation for Correctness Issues
  21 | 
  22 | When component isn't clear from the issue body:
  23 | 
  24 | 1. **Check comments first** - often contains debugging info
  25 | 2. **Look for information with backends:**
  26 | | Result | Label |
  27 | |--------|-------|
  28 | | Fails on `aot_eager`, not `eager` | `module: pt2-dispatcher` |
  29 | | Fails on `inductor`, not `aot_eager` | `module: inductor` |
  30 | | Fails during tracing (before backend) | `module: dynamo` |
  31 | 
  32 | ---
  33 | 
  34 | **This is critical** when you have identified an issue as inductor, and the failing device is "cpu" ONLY, then this is a CPU inductor issue, and should be redirected to `oncall: cpu inductor`
  35 | 
  36 | ## 3. Don't Over-Tag pt2-dispatcher
  37 | 
  38 | `module: pt2-dispatcher` is for bugs **IN** the dispatcher code, not just when it appears in a stack trace.
  39 | 
  40 | **Common mistake:** Seeing `_aot_autograd/` in a stack trace and assuming it's a pt2-dispatcher bug. The dispatcher code is on the call path for almost everything - that doesn't mean the bug is there.
  41 | 
  42 | **Only add pt2-dispatcher when:**
  43 | - The bug is clearly in AOT autograd logic (e.g., incorrect tensor metadata handling)
  44 | - The bug is in functionalization
  45 | - The bug is in FakeTensor implementation
  46 | - The bug is in custom operator registration/dispatch
  47 | 
  48 | **Don't add pt2-dispatcher when:**
  49 | - AOT autograd just happens to be on the stack trace
  50 | - The actual bug is in functorch transforms (use `module: functorch` instead)
  51 | - The actual bug is in inductor codegen (use `module: inductor` instead)
  52 | - You're not sure where the bug actually is
  53 | 
  54 | ---
  55 | 
  56 | ## 4. Don't Redirect When PT2 Owns the Code
  57 | 
  58 | **This is critical:** Don't redirect to another oncall just because their subsystem is *involved*. Only redirect when:
  59 | 1. The bug is clearly **IN** their code, AND
  60 | 2. PT2 code is not at fault
  61 | 
  62 | **Examples - DO NOT redirect:**
  63 | 
  64 | | Situation | Why NOT redirect |
  65 | |-----------|------------------|
  66 | | Export triggers a bug, but the bug is a leaked hook in AOT autograd | Bug is in PT2 code → PT2 owns it |
  67 | | DTensor has a bad error message under compile | Bug is in PT2's error handling → PT2 owns UX |
  68 | | Distributed training fails, but stack trace shows inductor issue | Bug is in inductor → PT2 owns it |
  69 | 
  70 | For PT2-D issues, you may also add `oncall: distributed` but DO NOT hand this off fully - keep the `oncall: pt2` label.
  71 | 
  72 | **Examples - DO redirect:**
  73 | 
  74 | | Situation | Why redirect |
  75 | |-----------|--------------|
  76 | | MKLDNN-specific codegen bug | `oncall: cpu inductor` owns MKLDNN |
  77 | | Export-only issue with no compile involvement | `oncall: export` owns it |
  78 | | Bug in DTensor's tensor subclass implementation | `oncall: distributed` owns DTensor internals |
  79 | 
  80 | **The test:** Ask "where would the fix need to be made?" If the fix is in PT2 code, PT2 owns it.
  81 | 
  82 | **Adding labels for visibility:** You CAN add domain labels (e.g., `module: dtensor`) so domain experts see the issue, but don't ADD the oncall redirect label unless you're actually handing it off.
  83 | 
  84 | **This is critical** when you have identified an issue as inductor, and the failing device is "cpu" ONLY, then this is a CPU inductor issue, and should be redirected to `oncall: cpu inductor`
  85 | 
  86 | ---
  87 | 
  88 | ## 5. Add Domain-Specific Labels for Visibility
  89 | 
  90 | Even when not redirecting, add labels so domain experts see the issue:
  91 | 
  92 | | Domain | Label |
  93 | |--------|-------|
  94 | | DTensor | `module: dtensor` |
  95 | | FSDP | `module: fsdp` |
  96 | | DDP | `module: ddp` |
  97 | | Flex attention | `module: flex attention` |
  98 | 
  99 | ---
 100 | 
 101 | ## 6. Use Feature-Specific Labels
 102 | 
 103 | Check for existing labels before inventing categories:
 104 | 
 105 | | Feature | Label |
 106 | |---------|-------|
 107 | | Caching issues | `compile-cache` |
 108 | | Determinism | `module: determinism` |
 109 | | Compile/startup time | `module: compile-time` |
 110 | | Numerical issues | `module: numerical-stability` |
 111 | | UX/error messages | `module: compile ux` |
 112 | 
 113 | ---
 114 | 
 115 | ## 7. functorch + compile
 116 | 
 117 | | Situation | Labels |
 118 | |-----------|--------|
 119 | | Compiling a functorch transform (vjp, grad, vmap) | `module: functorch`, `dynamo-functorch` |
 120 | | Only add `pt2-dispatcher` if stack trace shows AOT autograd | Check stack trace first |
 121 | 
 122 | ---
 123 | 
 124 | ## 8. High Priority Criteria
 125 | 
 126 | **This is critical** You should not explicitly add `high priority` - add `triage review` instead
 127 | so that it is reviewed at the next triage meeting by the oncall.
 128 | 
 129 | Mark `triage review` if ANY of these apply:
 130 | 
 131 | | Criteria | Example |
 132 | |----------|---------|
 133 | | **Crash** (segfault, illegal memory access) | Device-side assert, SIGSEGV |
 134 | | **Silently wrong results** | Output differs from eager with no error |
 135 | | **Regression** | "This used to work in version X" |
 136 | | **Flaky test** | Usually indicates regression |
 137 | | **Important model regressed** (>10% perf) | Common model, significant slowdown |
 138 | | **Important customer** | Huggingface, common usage patterns |
 139 | 
 140 | ---
 141 | 
 142 | ## 9. Fuzzer Issues
 143 | 
 144 | For `topic: fuzzer` issues:
 145 | 
 146 | 1. Ensure rtol/atol are at default tolerances
 147 | 2. Don't compare indices of max/min (avoids tolerance issues)
 148 | 3. Use `torch._dynamo.utils.same` with `fp64_ref` for comparison
 149 | 4. If criteria met and bug appears easy/common → triage normally
 150 | 5. If complex and rare → add `low priority`
 151 | 
 152 | ---
 153 | 
 154 | ## 10. Quick Label Reference
 155 | 
 156 | ### Core Components
 157 | - `module: dynamo` - Tracing, bytecode, graph breaks
 158 | - `module: inductor` - Codegen, Triton kernels
 159 | - `module: dynamic shapes` - Symbolic shapes, guards, data-dependent
 160 | - `module: pt2-dispatcher` - AOT autograd, functionalization, FakeTensor
 161 | - `module: cuda graphs` - CUDA graph capture/replay
 162 | - `module: flex attention` - Flex attention API
 163 | 
 164 | ### Holistic Areas
 165 | - `module: compile ux` - Error messages, APIs, programming model
 166 | - `module: startup-compile-tracing time` - Compilation speed
 167 | - `module: performance` - Runtime performance
 168 | - `module: memory usage` - Memory issues
 169 | 
 170 | ### Status Labels
 171 | - `triaged` - Done triaging
 172 | - `triage review` - Discuss at meeting
 173 | - `needs reproduction` - Blocked on repro
 174 | - `needs research` - Needs investigation
 175 | - `actionable` - Clear what to do
 176 | 
 177 | ### Redirects
 178 | - `oncall: cpu inductor` - CPU/MKLDNN issues
 179 | - `oncall: export` - Export-specific issues
 180 | - `oncall: distributed` - Distributed training issues
 181 | 
 182 | ### CPU Inductor Routing
 183 | 
 184 | Route to `oncall: cpu inductor` (not generic `oncall: pt2`) when the issue is specific to CPU backend in inductor:
 185 | - Title or body mentions `[CPU]`, `cpu`, or `MKLDNN`
 186 | - CPU-specific codegen bugs (e.g., float16 handling on CPU)
 187 | - Issues that only reproduce on CPU, not CUDA
 188 | - MKLDNN-specific kernel issues
 189 | 
 190 | Example: "[Inductor][CPU][float16] LayerNorm outputs NaN" → `oncall: cpu inductor`, NOT `oncall: pt2`
```


---
## .claude/skills/triaging-issues/scripts/add_bot_triaged.py

```
   1 | #!/usr/bin/env python3
   2 | """
   3 | PostToolUse hook to automatically add the bot-triaged label after any issue mutation.
   4 | 
   5 | This hook runs after successful GitHub issue mutations (label/comment/close/transfer)
   6 | and directly applies the `bot-triaged` label via the gh CLI.
   7 | 
   8 | Exit codes:
   9 |   0 - Success
  10 | """
  11 | 
  12 | import json
  13 | import os
  14 | import subprocess
  15 | import sys
  16 | from datetime import datetime
  17 | 
  18 | 
  19 | DEBUG_LOG = os.environ.get("TRIAGE_HOOK_DEBUG_LOG", "/tmp/triage_hooks.log")
  20 | BOT_TRIAGED_LABEL = "bot-triaged"
  21 | 
  22 | 
  23 | def debug_log(msg: str):
  24 |     """Append a debug message to the log file and stderr (for CI visibility)."""
  25 |     timestamp = datetime.now().isoformat()
  26 |     formatted = f"[{timestamp}] [PostToolUse] {msg}"
  27 |     try:
  28 |         with open(DEBUG_LOG, "a") as f:
  29 |             f.write(formatted + "\n")
  30 |     except Exception:
  31 |         pass
  32 |     if os.environ.get("TRIAGE_HOOK_VERBOSE"):
  33 |         print(f"[DEBUG] {formatted}", file=sys.stderr)
  34 | 
  35 | 
  36 | def main():
  37 |     try:
  38 |         data = json.load(sys.stdin)
  39 |         debug_log(f"Hook invoked with data: {json.dumps(data, indent=2)}")
  40 |         tool_input = data.get("tool_input", {})
  41 | 
  42 |         owner = tool_input.get("owner")
  43 |         repo = tool_input.get("repo")
  44 |         issue_number = tool_input.get("issue_number")
  45 | 
  46 |         if not all([owner, repo, issue_number]):
  47 |             debug_log(
  48 |                 f"Missing required fields - owner={owner}, repo={repo}, issue_number={issue_number}"
  49 |             )
  50 |             sys.exit(0)
  51 | 
  52 |         cmd = [
  53 |             "gh",
  54 |             "issue",
  55 |             "edit",
  56 |             str(issue_number),
  57 |             "--repo",
  58 |             f"{owner}/{repo}",
  59 |             "--add-label",
  60 |             BOT_TRIAGED_LABEL,
  61 |         ]
  62 |         debug_log(f"Running: {' '.join(cmd)}")
  63 |         result = subprocess.run(cmd, capture_output=True, check=False)
  64 |         debug_log(
  65 |             f"gh exit code: {result.returncode}, stderr: {result.stderr.decode()}"
  66 |         )
  67 |         sys.exit(0)
  68 | 
  69 |     except json.JSONDecodeError as e:
  70 |         debug_log(f"JSON decode error: {e}")
  71 |         sys.exit(0)
  72 |     except Exception as e:
  73 |         debug_log(f"Unexpected error: {e}")
  74 |         sys.exit(0)
  75 | 
  76 | 
  77 | if __name__ == "__main__":
  78 |     main()
```


---
## .claude/skills/triaging-issues/scripts/validate_labels.py

```
   1 | #!/usr/bin/env python3
   2 | """
   3 | PreToolUse hook to validate and sanitize labels during triage.
   4 | 
   5 | This hook intercepts mcp__github__update_issue calls and:
   6 | 1. Strips forbidden labels (CI/infrastructure/severity)
   7 | 2. Strips non-existent labels (not in labels.json)
   8 | 3. Strips redundant labels (e.g. module: nn when module: rnn is present)
   9 | 4. Fetches existing labels on the issue and merges with valid new labels
  10 | 5. Rewrites the tool input via updatedInput so the MCP SET preserves existing labels
  11 | 
  12 | Exit codes:
  13 |   0 - Allow the tool call (with possible input rewrite via stdout JSON)
  14 |   2 - Block the tool call (feedback sent to Claude)
  15 | """
  16 | 
  17 | import json
  18 | import os
  19 | import re
  20 | import subprocess
  21 | import sys
  22 | from datetime import datetime
  23 | from pathlib import Path
  24 | 
  25 | 
  26 | DEBUG_LOG = os.environ.get("TRIAGE_HOOK_DEBUG_LOG", "/tmp/triage_hooks.log")
  27 | SCRIPT_DIR = Path(__file__).parent
  28 | LABELS_FILE = SCRIPT_DIR.parent / "labels.json"
  29 | 
  30 | FORBIDDEN_PATTERNS = [
  31 |     r"^ciflow/",
  32 |     r"^test-config/",
  33 |     r"^release notes:",
  34 |     r"^ci-",
  35 |     r"^ci:",
  36 |     r"^sev",
  37 |     r"deprecated",
  38 | ]
  39 | 
  40 | FORBIDDEN_EXACT = [
  41 |     "merge blocking",
  42 |     "oncall: releng",  # Not a triage redirect target; use module: ci instead
  43 | ]
  44 | 
  45 | REDUNDANT_PAIRS = [
  46 |     ("module: rnn", "module: nn"),
  47 | ]
  48 | 
  49 | 
  50 | def debug_log(msg: str, to_stderr: bool = False):
  51 |     timestamp = datetime.now().isoformat()
  52 |     formatted = f"[{timestamp}] [PreToolUse] {msg}"
  53 |     try:
  54 |         with open(DEBUG_LOG, "a") as f:
  55 |             f.write(formatted + "\n")
  56 |     except Exception:
  57 |         pass
  58 |     if to_stderr or os.environ.get("TRIAGE_HOOK_VERBOSE"):
  59 |         print(f"[DEBUG] {formatted}", file=sys.stderr)
  60 | 
  61 | 
  62 | def is_forbidden(label: str) -> bool:
  63 |     label_lower = label.lower()
  64 |     for pattern in FORBIDDEN_PATTERNS:
  65 |         if re.search(pattern, label_lower):
  66 |             return True
  67 |     return label_lower in [f.lower() for f in FORBIDDEN_EXACT]
  68 | 
  69 | 
  70 | def load_valid_labels() -> set[str]:
  71 |     try:
  72 |         with open(LABELS_FILE) as f:
  73 |             data = json.load(f)
  74 |     except FileNotFoundError:
  75 |         raise RuntimeError(f"labels.json not found at {LABELS_FILE}") from None
  76 |     except json.JSONDecodeError as e:
  77 |         raise RuntimeError(f"labels.json contains invalid JSON: {e}") from None
  78 |     except PermissionError:
  79 |         raise RuntimeError("Cannot read labels.json: permission denied") from None
  80 | 
  81 |     labels_list = data.get("labels", [])
  82 |     try:
  83 |         return {label["name"] for label in labels_list}
  84 |     except (KeyError, TypeError) as e:
  85 |         raise RuntimeError(f"labels.json has malformed entries: {e}") from None
  86 | 
  87 | 
  88 | def strip_redundant(labels: list[str]) -> tuple[list[str], list[str]]:
  89 |     labels_set = set(labels)
  90 |     to_remove = set()
  91 |     for specific, general in REDUNDANT_PAIRS:
  92 |         if specific in labels_set and general in labels_set:
  93 |             to_remove.add(general)
  94 |     return [l for l in labels if l not in to_remove], sorted(to_remove)
  95 | 
  96 | 
  97 | def fetch_existing_labels(owner: str, repo: str, issue_number: int) -> list[str]:
  98 |     result = subprocess.run(
  99 |         [
 100 |             "gh",
 101 |             "issue",
 102 |             "view",
 103 |             str(issue_number),
 104 |             "--repo",
 105 |             f"{owner}/{repo}",
 106 |             "--json",
 107 |             "labels",
 108 |         ],
 109 |         capture_output=True,
 110 |         text=True,
 111 |         check=False,
 112 |         timeout=15,
 113 |     )
 114 |     if result.returncode != 0:
 115 |         raise RuntimeError(
 116 |             f"Cannot fetch existing labels (gh exit {result.returncode}): "
 117 |             f"{result.stderr.strip()}"
 118 |         )
 119 |     data = json.loads(result.stdout)
 120 |     return [label["name"] for label in data.get("labels", [])]
 121 | 
 122 | 
 123 | def allow_with_updated_input(tool_input: dict, merged_labels: list[str]) -> None:
 124 |     updated = dict(tool_input)
 125 |     updated["labels"] = merged_labels
 126 |     json.dump(
 127 |         {
 128 |             "hookSpecificOutput": {
 129 |                 "hookEventName": "PreToolUse",
 130 |                 "permissionDecision": "allow",
 131 |                 "updatedInput": updated,
 132 |             }
 133 |         },
 134 |         sys.stdout,
 135 |     )
 136 |     sys.exit(0)
 137 | 
 138 | 
 139 | def main():
 140 |     try:
 141 |         data = json.load(sys.stdin)
 142 |         debug_log(f"Hook invoked with data: {json.dumps(data, indent=2)}")
 143 |         tool_input = data.get("tool_input", {})
 144 | 
 145 |         requested_labels = tool_input.get("labels", []) or []
 146 |         debug_log(f"Labels requested: {requested_labels}")
 147 | 
 148 |         if not requested_labels:
 149 |             debug_log("No labels provided, allowing")
 150 |             sys.exit(0)
 151 | 
 152 |         owner = tool_input.get("owner", "pytorch")
 153 |         repo = tool_input.get("repo", "pytorch")
 154 |         issue_number = tool_input.get("issue_number")
 155 |         if not issue_number:
 156 |             raise RuntimeError("tool_input missing issue_number")
 157 | 
 158 |         forbidden = [l for l in requested_labels if is_forbidden(l)]
 159 |         clean_labels = [l for l in requested_labels if not is_forbidden(l)]
 160 | 
 161 |         if forbidden:
 162 |             debug_log(f"Stripped forbidden labels: {forbidden}")
 163 |             if not clean_labels:
 164 |                 clean_labels = ["triage review"]
 165 |             elif "triage review" not in clean_labels:
 166 |                 clean_labels.append("triage review")
 167 |             print(
 168 |                 f"Stripped forbidden labels (require human decision): {forbidden}. "
 169 |                 f"Added 'triage review' for human attention.",
 170 |                 file=sys.stderr,
 171 |             )
 172 | 
 173 |         valid_labels = load_valid_labels()
 174 |         nonexistent = [l for l in clean_labels if l not in valid_labels]
 175 |         clean_labels = [l for l in clean_labels if l in valid_labels]
 176 | 
 177 |         if nonexistent:
 178 |             debug_log(f"Stripped non-existent labels: {nonexistent}")
 179 |             print(
 180 |                 f"Stripped non-existent labels: {nonexistent}",
 181 |                 file=sys.stderr,
 182 |             )
 183 | 
 184 |         clean_labels, removed_redundant = strip_redundant(clean_labels)
 185 |         if removed_redundant:
 186 |             debug_log(f"Stripped redundant labels: {removed_redundant}")
 187 |             print(
 188 |                 f"Stripped redundant labels: {removed_redundant}",
 189 |                 file=sys.stderr,
 190 |             )
 191 | 
 192 |         if not clean_labels:
 193 |             debug_log("No valid labels remain after filtering, blocking")
 194 |             print(
 195 |                 "All requested labels were invalid. No labels to apply.",
 196 |                 file=sys.stderr,
 197 |             )
 198 |             sys.exit(2)
 199 | 
 200 |         existing_labels = fetch_existing_labels(owner, repo, issue_number)
 201 |         debug_log(f"Existing labels on issue: {existing_labels}")
 202 | 
 203 |         merged = sorted(set(existing_labels) | set(clean_labels))
 204 |         debug_log(f"Merged labels (existing + new): {merged}")
 205 | 
 206 |         allow_with_updated_input(tool_input, merged)
 207 | 
 208 |     except json.JSONDecodeError as e:
 209 |         debug_log(f"JSON decode error: {e}")
 210 |         print(f"Hook error: Invalid JSON input: {e}", file=sys.stderr)
 211 |         print("Hook was unable to validate labels; stopping triage.", file=sys.stderr)
 212 |         sys.exit(2)
 213 |     except Exception as e:
 214 |         debug_log(f"Unexpected error: {type(e).__name__}: {e}")
 215 |         print(f"Hook error: {e}", file=sys.stderr)
 216 |         print("Hook was unable to validate labels; stopping triage.", file=sys.stderr)
 217 |         sys.exit(2)
 218 | 
 219 | 
 220 | if __name__ == "__main__":
 221 |     main()
```


---
## .claude/skills/triaging-issues/templates.json

```
   1 | {
   2 |   "description": "Standard response templates for issue triage actions",
   3 |   "templates": {
   4 |     "redirect_to_forum": {
   5 |       "action": "Close issue and add comment",
   6 |       "use_when": "Issue is a usage question, not a bug report or feature request",
   7 |       "comment": "Thank you for your interest in PyTorch! This issue appears to be a usage question rather than a bug report or feature request.\n\nFor usage questions, please use the [PyTorch Discussion Forum](https://discuss.pytorch.org/) where you'll get help from both the community and PyTorch maintainers.\n\nClosing this issue, but feel free to reopen if you believe this is actually a bug or feature request."
   8 |     },
   9 |     "request_more_info": {
  10 |       "action": "Add comment and stop",
  11 |       "use_when": "Classification is unclear and more details are needed to decide between question vs bug/feature",
  12 |       "comment": "Thanks for the report. To triage this, could you share:\n\n- A minimal repro (small script or steps)\n- Full error logs / stack trace\n- Output of `collect_env.py`\n\nOnce we have that, we can classify and route this properly."
  13 |     },
  14 |     "needs_reproduction": {
  15 |       "action": "Edit issue to remove external links, add label 'needs reproduction', and comment",
  16 |       "use_when": "Issue requires downloading external files (.zip, .pt, .pth, .pkl, .safetensors, .onnx, .bin) or links to external storage (Google Drive, Dropbox, OneDrive, Mega, WeTransfer, Hugging Face Hub model files) to reproduce",
  17 |       "comment": "Thanks for the report! To help us investigate:\n\n1. Can you reproduce this without the external files? (e.g., using random weights or synthetic data)\n2. Are there any extreme or special values in the weights/inputs? (e.g., very large values, NaN, inf)\n\nA self-contained script that doesn't require downloading files helps maintainers reproduce and debug the issue faster."
  18 |     },
  19 |     "numerical_accuracy": {
  20 |       "action": "Add comment when labeling with 'module: edge cases' or closing numerical accuracy issues",
  21 |       "use_when": "Issue involves extremal values (near torch.finfo.max/min), numerical precision differences between backends, or expected floating point behavior",
  22 |       "comment": "This appears to be related to numerical accuracy limitations in floating point computation. PyTorch documents expected behavior for extremal values and precision differences in the [Numerical Accuracy](https://docs.pytorch.org/docs/stable/notes/numerical_accuracy.html) documentation.\n\nKey points:\n- Floating point provides limited accuracy (~7 decimal digits for fp32, ~16 for fp64)\n- Results may differ between CPU and GPU backends\n- Extremal values (near dtype max/min) can cause overflow in intermediate computations\n\nIf you believe this is a bug beyond expected numerical behavior, please provide a reproducer with values well within the normal range."
  23 |     }
  24 |   }
  25 | }
```


---
## .github/copilot-instructions.md

```
   1 | # PyTorch Copilot Instructions
   2 | 
   3 | This is the PyTorch machine learning framework codebase. These instructions help AI agents navigate and contribute effectively.
   4 | 
   5 | ## Architecture Overview
   6 | 
   7 | ### Core Components
   8 | 
   9 | - **c10/** - Core library (C++-10 compatible) for essential, binary-size-conscious functionality
  10 | - **aten/** - ATen tensor library (C++), PyTorch's foundation without autograd
  11 |   - `aten/src/ATen/native/` - Modern operator implementations (CPU/CUDA/MPS/sparse)
  12 |   - `aten/src/ATen/native/native_functions.yaml` - **Critical**: Declarative operator registry
  13 | - **torch/** - Python bindings and public API
  14 |   - `torch/csrc/` - C++ Python bindings (hand-written and generated)
  15 |   - `torch/csrc/autograd/` - Reverse-mode automatic differentiation
  16 |   - `torch/csrc/jit/` - TorchScript JIT compiler
  17 | - **torchgen/** - Code generation tooling that reads `native_functions.yaml`
  18 | - **tools/** - Build scripts, autograd derivatives, code generation
  19 | 
  20 | ### The Code Generation Workflow
  21 | 
  22 | **Most operator changes require editing `native_functions.yaml`**, not direct C++ files. This YAML file:
  23 | 1. Declares operator signatures, variants (function/method), and dispatch behavior
  24 | 2. Gets processed by `torchgen/` to generate C++/Python bindings
  25 | 3. Produces headers in `build/aten/src/ATen/` during compilation
  26 | 
  27 | Example entry structure:
  28 | ```yaml
  29 | - func: my_op(Tensor self, Scalar alpha=1) -> Tensor
  30 |   variants: function, method
  31 |   dispatch:
  32 |     CPU: my_op_cpu
  33 |     CUDA: my_op_cuda
  34 | ```
  35 | 
  36 | After editing `native_functions.yaml`, implement kernels in `aten/src/ATen/native/` (see `aten/src/ATen/native/README.md`).
  37 | 
  38 | ## Development Workflows
  39 | 
  40 | ### Building from Source
  41 | 
  42 | **Never run `setup.py` directly** - use pip with editable install:
  43 | ```bash
  44 | python -m pip install --no-build-isolation -v -e .
  45 | ```
  46 | 
  47 | Speed up builds:
  48 | - `DEBUG=1` - Debug symbols with `-g -O0`
  49 | - `USE_CUDA=0` - Skip CUDA compilation
  50 | - `BUILD_TEST=0` - Skip C++ test binaries
  51 | - Install `ninja` (`pip install ninja`) for faster builds
  52 | - Use `ccache` for incremental compilation caching
  53 | 
  54 | Rebuild specific targets: `(cd build && ninja <target>)`
  55 | 
  56 | ### Testing
  57 | 
  58 | **Critical**: DO NOT run entire test suites. Run specific tests only:
  59 | ```bash
  60 | python test/test_torch.py TestTorch.test_specific_case
  61 | ```
  62 | 
  63 | **Test structure**: All tests use `torch.testing._internal.common_utils`:
  64 | ```python
  65 | from torch.testing._internal.common_utils import run_tests, TestCase
  66 | 
  67 | class TestFeature(TestCase):
  68 |     def test_something(self):
  69 |         # Use self.assertEqual for tensor comparisons
  70 |         pass
  71 | 
  72 | if __name__ == "__main__":
  73 |     run_tests()
  74 | ```
  75 | 
  76 | **For bug fixes**: Create a standalone reproduction script first, verify it fails, then fix and add to appropriate test file.
  77 | 
  78 | ### Linting
  79 | 
  80 | Run linter (not pre-commit): `lintrunner -a` (auto-applies fixes)
  81 | 
  82 | ## Project-Specific Conventions
  83 | 
  84 | ### Memory and Storage
  85 | - **Storage is never nullptr** (but `StorageImpl.data` may be nullptr for unallocated outputs)
  86 | - CUDA device info lives in storage objects
  87 | 
  88 | ### Python-C++ Integration (`torch/csrc/`)
  89 | - Always include `Python.h` **first** to avoid `_XOPEN_SOURCE` redefinition errors
  90 | - Use `pybind11::gil_scoped_acquire` before calling Python API or using `THPObjectPtr`
  91 | - Wrap entry points with `HANDLE_TH_ERRORS` / `END_HANDLE_TH_ERRORS` for exception conversion
  92 | 
  93 | ### Dispatch System
  94 | - PyTorch uses operator dispatch to route calls to backend-specific kernels
  95 | - Prefer `CompositeExplicitAutograd` dispatch when writing device-agnostic compound ops
  96 | - See `aten/src/ATen/native/README.md` for dispatch keyword guidance
  97 | 
  98 | ## Git Workflow (AI Agent Specific)
  99 | 
 100 | When preparing PRs from this environment:
 101 | ```bash
 102 | git stash -u
 103 | git reset --hard $(cat /tmp/orig_work.txt)  # Reset to LOCAL branch
 104 | git stash pop
 105 | # Resolve conflicts if necessary
 106 | ```
 107 | 
 108 | ## Common Gotchas
 109 | 
 110 | 1. **Editing generated files** - If it's in `build/`, don't edit it. Edit the source template or `native_functions.yaml`
 111 | 2. **NVCC template compilation** - NVCC is stricter about C++ than gcc/clang; code working on Linux may fail Windows CI
 112 | 3. **Windows symbol visibility** - Use `TORCH_API` macros for exported symbols (required on Windows, optional on Linux)
 113 | 4. **No internet access** - DO NOT attempt to install dependencies during development
 114 | 
 115 | ## Key Files Reference
 116 | 
 117 | - `AGENTS.md` - Instructions specific to AI coding agents
 118 | - `CONTRIBUTING.md` - Comprehensive human contributor guide
 119 | - `GLOSSARY.md` - Terminology (ATen, kernels, operations, JIT, TorchScript)
 120 | - `aten/src/ATen/native/README.md` - Operator implementation guide
 121 | - `tools/autograd/derivatives.yaml` - Gradient definitions for autograd
 122 | 
 123 | ## Performance Debugging
 124 | 
 125 | Use `TORCH_SHOW_CPP_STACKTRACES=1` for C++ traces in Python errors. For profiling, prefer `py-spy` over manual instrumentation.
```


---
## AGENTS.md

```
   1 | - This is the only AGENTS.md, there are no recursive AGENTS.md
   2 | - When you are working on a bug, first create a standalone file that
   3 |   reproduces the bug and verify it fails in the expected way.  Use this to
   4 |   test if your changes work.  Once the change is passing, find an appropriate
   5 |   test file to add the test to and make sure to follow local conventions on
   6 |   the test file.
   7 | - If you are running the real test suite, DO NOT run the entire test suite.
   8 |   Instead run only a single test case, e.g., 'python test/test_torch.py TestTorch.test_dir'
   9 | - Do NOT run setup.py, you do not have a working build environment
  10 | - Do NOT run pre-commit, it is not setup
  11 | - To run lint, run 'lintrunner -a' (which will autoapply changes)
  12 | - Do NOT attempt to install dependencies, you do not have Internet access
  13 | - Do NOT create summary files unless explicitly asked
  14 | - When you are ready to make a PR, do exactly these steps:
  15 |   - git stash -u
  16 |   - git reset --hard $(cat /tmp/orig_work.txt) # NB: reset to the LOCAL branch, do NOT fetch
  17 |   - git stash pop
  18 |   - Resolve conflicts if necessary
```


---
## CLAUDE.md

```
   1 | # PR Review
   2 | 
   3 | When asked to review a PR, always use the /pr-review skill.
   4 | 
   5 | # Environment
   6 | 
   7 | If any tool you're trying to use (pip, python, spin, etc) is missing, always stop and ask the user if an environment is needed. Do NOT try to find alternatives or install these tools.
   8 | 
   9 | # Build
  10 | 
  11 | Always ask for build configuration environment variables before running build.
  12 | All build (both codegen, C++ and python) is done via `pip install -e . -v --no-build-isolation`.
  13 | You should NEVER run any other command to build PyTorch.
  14 | 
  15 | # Testing
  16 | 
  17 | Use our test class and test runner:
  18 | 
  19 | ```
  20 | from torch.testing._internal.common_utils import run_tests, TestCase
  21 | 
  22 | class TestFeature(TestCase):
  23 |     ...
  24 | 
  25 | if __name__ == "__main__":
  26 |     run_tests()
  27 | ```
  28 | 
  29 | To test Tensor equality, use assertEqual.
  30 | For tests over multiple inputs, use the `@parametrize` decorator.
  31 | For any test that checks numerics of the on-device implementation, use `instantiate_device_type_tests` to write device-generic tests.
  32 | 
  33 | # Linting
  34 | 
  35 | Only use commands provided via `spin` for linting.
  36 | Use `spin help` to list available commands.
  37 | Generally, use `spin lint` as to run the lint and `spin fixlint` to apply automatic fixes.
  38 | 
  39 | # Commit messages
  40 | 
  41 | Don't commit unless the user explicitly asks you to.
  42 | 
  43 | When writing a commit message, don't make a bullet list of the individual
  44 | changes. Instead, if the PR is large, explain the order to review changes
  45 | (e.g., the logical progression), or if it's short just omit the bullet list
  46 | entirely.
  47 | 
  48 | Disclose that the PR was authored with Claude.
  49 | 
  50 | If a commit message contains `ghstack-source-id` or `Pull-Request` trailers,
  51 | you MUST preserve them when rewriting or splitting commit messages. ghstack
  52 | will update the source id automatically when needed.
  53 | 
  54 | # Coding Style Guidelines
  55 | 
  56 | Follow these rules for all code changes in this repository:
  57 | 
  58 | - Minimize comments; be concise; code should be self-explanatory and self-documenting.
  59 | - Comments should be useful, for example, comments that remind the reader about
  60 |   some global context that is non-obvious and can't be inferred locally.
  61 | - Don't make trivial (1-2 LOC) helper functions that are only used once unless
  62 |   it significantly improves code readability.
  63 | - Prefer clear abstractions. State management should be explicit.
  64 |   For example, if managing state in a Python class: there should be a clear
  65 |   class definition that has all of the members: don't dynamically `setattr`
  66 |   a field on an object and then dynamically `getattr` the field on the object.
  67 | - Match existing code style and architectural patterns.
  68 | - Assume the reader has familiarity with PyTorch. They may not be the expert
  69 |   on the code that is being read, but they should have some experience in the
  70 |   area.
  71 | 
  72 | If uncertain, choose the simpler, more concise implementation.
  73 | 
  74 | # Dynamo Config
  75 | 
  76 | Use `torch._dynamo.config.patch` for temporarily changing config. It can be used as a decorator on test methods or as a context manager:
  77 | 
  78 | ```python
  79 | # Good - use patch as decorator on test method
  80 | @torch._dynamo.config.patch(force_compile_during_fx_trace=True)
  81 | def test_my_feature(self):
  82 |     # test code here
  83 |     pass
  84 | 
  85 | # Good - use patch as context manager
  86 | with torch._dynamo.config.patch(force_compile_during_fx_trace=True):
  87 |     # test code here
  88 |     pass
  89 | 
  90 | # Bad - manual save/restore
  91 | orig = torch._dynamo.config.force_compile_during_fx_trace
  92 | try:
  93 |     torch._dynamo.config.force_compile_during_fx_trace = True
  94 |     # test code here
  95 | finally:
  96 |     torch._dynamo.config.force_compile_during_fx_trace = orig
  97 | ```
  98 | 
  99 | # Fixing B950 line too long in multi-line string blocks
 100 | 
 101 | If B950 line too long triggers on a multi-line string block, you cannot fix it by
 102 | putting # noqa: B950 on that line directly, as that would change the meaning of the
 103 | string, nor can you fix it by line breaking the string (since you need the string
 104 | to stay the same).  Instead, put # noqa: B950 on the same line as the terminating
 105 | triple quote.
 106 | 
 107 | Example:
 108 | 
 109 | ```
 110 |     self.assertExpectedInline(
 111 |         foo(),
 112 |         """
 113 | this line is too long...
 114 | """,  # noqa: B950
 115 |     )
 116 | ```
 117 | 
 118 | # Logging and Structured Tracing
 119 | 
 120 | When adding debug logging for errors or diagnostic info, consider two user personas:
 121 | 
 122 | 1. **Local development**: Users run locally and can access files on disk
 123 | 2. **Production jobs**: Users can only access logs via `tlparse` from structured traces
 124 | 
 125 | For production debugging, use `trace_structured` to log artifacts:
 126 | 
 127 | ```python
 128 | from torch._logging import trace_structured
 129 | 
 130 | # Log an artifact (graph, edge list, etc.)
 131 | trace_structured(
 132 |     "artifact",
 133 |     metadata_fn=lambda: {
 134 |         "name": "my_debug_artifact",
 135 |         "encoding": "string",
 136 |     },
 137 |     payload_fn=lambda: my_content_string,
 138 | )
 139 | ```
 140 | 
 141 | To check if structured tracing is enabled (for conditional messaging):
 142 | 
 143 | ```python
 144 | from torch._logging._internal import trace_log
 145 | 
 146 | if trace_log.handlers:
 147 |     # Structured tracing is enabled, suggest tlparse in error messages
 148 |     msg += "[Use tlparse to extract debug artifacts]"
 149 | ```
 150 | 
 151 | **Best practices for error diagnostics:**
 152 | 
 153 | - Always log to `trace_structured` for production (no runtime cost if disabled)
 154 | - If you're dumping debug info in the event of a true internal compiler exception,
 155 |   you can also consider writing to local files for local debugging convenience
 156 | - In error messages, tell users about both options:
 157 |   - Local files: "FX graph dump: min_cut_failed_graph.txt"
 158 |   - Production: "Use tlparse to extract artifacts" (only if tracing enabled)
 159 | - Use `_get_unique_path()` pattern to avoid overwriting existing debug files
```


---
## README.md

```
   1 | ![PyTorch Logo](https://github.com/pytorch/pytorch/raw/main/docs/source/_static/img/pytorch-logo-dark.png)
   2 | 
   3 | --------------------------------------------------------------------------------
   4 | 
   5 | PyTorch is a Python package that provides two high-level features:
   6 | - Tensor computation (like NumPy) with strong GPU acceleration
   7 | - Deep neural networks built on a tape-based autograd system
   8 | 
   9 | You can reuse your favorite Python packages such as NumPy, SciPy, and Cython to extend PyTorch when needed.
  10 | 
  11 | Our trunk health (Continuous Integration signals) can be found at [hud.pytorch.org](https://hud.pytorch.org/ci/pytorch/pytorch/main).
  12 | 
  13 | <!-- toc -->
  14 | 
  15 | - [More About PyTorch](#more-about-pytorch)
  16 |   - [A GPU-Ready Tensor Library](#a-gpu-ready-tensor-library)
  17 |   - [Dynamic Neural Networks: Tape-Based Autograd](#dynamic-neural-networks-tape-based-autograd)
  18 |   - [Python First](#python-first)
  19 |   - [Imperative Experiences](#imperative-experiences)
  20 |   - [Fast and Lean](#fast-and-lean)
  21 |   - [Extensions Without Pain](#extensions-without-pain)
  22 | - [Installation](#installation)
  23 |   - [Binaries](#binaries)
  24 |     - [NVIDIA Jetson Platforms](#nvidia-jetson-platforms)
  25 |   - [From Source](#from-source)
  26 |     - [Prerequisites](#prerequisites)
  27 |       - [NVIDIA CUDA Support](#nvidia-cuda-support)
  28 |       - [AMD ROCm Support](#amd-rocm-support)
  29 |       - [Intel GPU Support](#intel-gpu-support)
  30 |     - [Get the PyTorch Source](#get-the-pytorch-source)
  31 |     - [Install Dependencies](#install-dependencies)
  32 |     - [Install PyTorch](#install-pytorch)
  33 |       - [Adjust Build Options (Optional)](#adjust-build-options-optional)
  34 |   - [Docker Image](#docker-image)
  35 |     - [Using pre-built images](#using-pre-built-images)
  36 |     - [Building the image yourself](#building-the-image-yourself)
  37 |   - [Building the Documentation](#building-the-documentation)
  38 |     - [Troubleshooting CI Errors](#troubleshooting-ci-errors)
  39 |     - [Building a PDF](#building-a-pdf)
  40 |   - [Previous Versions](#previous-versions)
  41 | - [Getting Started](#getting-started)
  42 | - [Resources](#resources)
  43 | - [Communication](#communication)
  44 | - [Releases and Contributing](#releases-and-contributing)
  45 | - [The Team](#the-team)
  46 | - [License](#license)
  47 | 
  48 | <!-- tocstop -->
  49 | 
  50 | ## More About PyTorch
  51 | 
  52 | [Learn the basics of PyTorch](https://pytorch.org/tutorials/beginner/basics/intro.html)
  53 | 
  54 | At a granular level, PyTorch is a library that consists of the following components:
  55 | 
  56 | | Component | Description |
  57 | | ---- | --- |
  58 | | [**torch**](https://pytorch.org/docs/stable/torch.html) | A Tensor library like NumPy, with strong GPU support |
  59 | | [**torch.autograd**](https://pytorch.org/docs/stable/autograd.html) | A tape-based automatic differentiation library that supports all differentiable Tensor operations in torch |
  60 | | [**torch.jit**](https://pytorch.org/docs/stable/jit.html) | A compilation stack (TorchScript) to create serializable and optimizable models from PyTorch code  |
  61 | | [**torch.nn**](https://pytorch.org/docs/stable/nn.html) | A neural networks library deeply integrated with autograd designed for maximum flexibility |
  62 | | [**torch.multiprocessing**](https://pytorch.org/docs/stable/multiprocessing.html) | Python multiprocessing, but with magical memory sharing of torch Tensors across processes. Useful for data loading and Hogwild training |
  63 | | [**torch.utils**](https://pytorch.org/docs/stable/data.html) | DataLoader and other utility functions for convenience |
  64 | 
  65 | Usually, PyTorch is used either as:
  66 | 
  67 | - A replacement for NumPy to use the power of GPUs.
  68 | - A deep learning research platform that provides maximum flexibility and speed.
  69 | 
  70 | Elaborating Further:
  71 | 
  72 | ### A GPU-Ready Tensor Library
  73 | 
  74 | If you use NumPy, then you have used Tensors (a.k.a. ndarray).
  75 | 
  76 | ![Tensor illustration](https://github.com/pytorch/pytorch/raw/main/docs/source/_static/img/tensor_illustration.png)
  77 | 
  78 | PyTorch provides Tensors that can live either on the CPU or the GPU and accelerates the
  79 | computation by a huge amount.
  80 | 
  81 | We provide a wide variety of tensor routines to accelerate and fit your scientific computation needs
  82 | such as slicing, indexing, mathematical operations, linear algebra, reductions.
  83 | And they are fast!
  84 | 
  85 | ### Dynamic Neural Networks: Tape-Based Autograd
  86 | 
  87 | PyTorch has a unique way of building neural networks: using and replaying a tape recorder.
  88 | 
  89 | Most frameworks such as TensorFlow, Theano, Caffe, and CNTK have a static view of the world.
  90 | One has to build a neural network and reuse the same structure again and again.
  91 | Changing the way the network behaves means that one has to start from scratch.
  92 | 
  93 | With PyTorch, we use a technique called reverse-mode auto-differentiation, which allows you to
  94 | change the way your network behaves arbitrarily with zero lag or overhead. Our inspiration comes
  95 | from several research papers on this topic, as well as current and past work such as
  96 | [torch-autograd](https://github.com/twitter/torch-autograd),
  97 | [autograd](https://github.com/HIPS/autograd),
  98 | [Chainer](https://chainer.org), etc.
  99 | 
 100 | While this technique is not unique to PyTorch, it's one of the fastest implementations of it to date.
 101 | You get the best of speed and flexibility for your crazy research.
 102 | 
 103 | ![Dynamic graph](https://github.com/pytorch/pytorch/raw/main/docs/source/_static/img/dynamic_graph.gif)
 104 | 
 105 | ### Python First
 106 | 
 107 | PyTorch is not a Python binding into a monolithic C++ framework.
 108 | It is built to be deeply integrated into Python.
 109 | You can use it naturally like you would use [NumPy](https://www.numpy.org/) / [SciPy](https://www.scipy.org/) / [scikit-learn](https://scikit-learn.org) etc.
 110 | You can write your new neural network layers in Python itself, using your favorite libraries
 111 | and use packages such as [Cython](https://cython.org/) and [Numba](http://numba.pydata.org/).
 112 | Our goal is to not reinvent the wheel where appropriate.
 113 | 
 114 | ### Imperative Experiences
 115 | 
 116 | PyTorch is designed to be intuitive, linear in thought, and easy to use.
 117 | When you execute a line of code, it gets executed. There isn't an asynchronous view of the world.
 118 | When you drop into a debugger or receive error messages and stack traces, understanding them is straightforward.
 119 | The stack trace points to exactly where your code was defined.
 120 | We hope you never spend hours debugging your code because of bad stack traces or asynchronous and opaque execution engines.
 121 | 
 122 | ### Fast and Lean
 123 | 
 124 | PyTorch has minimal framework overhead. We integrate acceleration libraries
 125 | such as [Intel MKL](https://software.intel.com/mkl) and NVIDIA ([cuDNN](https://developer.nvidia.com/cudnn), [NCCL](https://developer.nvidia.com/nccl)) to maximize speed.
 126 | At the core, its CPU and GPU Tensor and neural network backends
 127 | are mature and have been tested for years.
 128 | 
 129 | Hence, PyTorch is quite fast — whether you run small or large neural networks.
 130 | 
 131 | The memory usage in PyTorch is extremely efficient compared to Torch or some of the alternatives.
 132 | We've written custom memory allocators for the GPU to make sure that
 133 | your deep learning models are maximally memory efficient.
 134 | This enables you to train bigger deep learning models than before.
 135 | 
 136 | ### Extensions Without Pain
 137 | 
 138 | Writing new neural network modules, or interfacing with PyTorch's Tensor API, was designed to be straightforward
 139 | and with minimal abstractions.
 140 | 
 141 | You can write new neural network layers in Python using the torch API
 142 | [or your favorite NumPy-based libraries such as SciPy](https://pytorch.org/tutorials/advanced/numpy_extensions_tutorial.html).
 143 | 
 144 | If you want to write your layers in C/C++, we provide a convenient extension API that is efficient and with minimal boilerplate.
 145 | No wrapper code needs to be written. You can see [a tutorial here](https://pytorch.org/tutorials/advanced/cpp_extension.html) and [an example here](https://github.com/pytorch/extension-cpp).
 146 | 
 147 | 
 148 | ## Installation
 149 | 
 150 | ### Binaries
 151 | Commands to install binaries via Conda or pip wheels are on our website: [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)
 152 | 
 153 | 
 154 | #### NVIDIA Jetson Platforms
 155 | 
 156 | Python wheels for NVIDIA's Jetson Nano, Jetson TX1/TX2, Jetson Xavier NX/AGX, and Jetson AGX Orin are provided [here](https://forums.developer.nvidia.com/t/pytorch-for-jetson-version-1-10-now-available/72048) and the L4T container is published [here](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-pytorch)
 157 | 
 158 | They require JetPack 4.2 and above, and [@dusty-nv](https://github.com/dusty-nv) and [@ptrblck](https://github.com/ptrblck) are maintaining them.
 159 | 
 160 | 
 161 | ### From Source
 162 | 
 163 | #### Prerequisites
 164 | If you are installing from source, you will need:
 165 | - Python 3.10 or later
 166 | - A compiler that fully supports C++20, such as clang or gcc (gcc 11.3.0 or newer is required, on Linux)
 167 | - Visual Studio or Visual Studio Build Tool (Windows only)
 168 | - At least 10 GB of free disk space
 169 | - 30-60 minutes for the initial build (subsequent rebuilds are much faster)
 170 | 
 171 | \* PyTorch CI uses Visual C++ BuildTools, which come with Visual Studio Enterprise,
 172 | Professional, or Community Editions. You can also install the build tools from
 173 | https://visualstudio.microsoft.com/visual-cpp-build-tools/. The build tools *do not*
 174 | come with Visual Studio Code by default.
 175 | 
 176 | An example of environment setup is shown below:
 177 | 
 178 | * Linux:
 179 | 
 180 | ```bash
 181 | $ source <CONDA_INSTALL_DIR>/bin/activate
 182 | $ conda create -y -n <CONDA_NAME>
 183 | $ conda activate <CONDA_NAME>
 184 | ```
 185 | * Windows:
 186 | 
 187 | ```bash
 188 | $ source <CONDA_INSTALL_DIR>\Scripts\activate.bat
 189 | $ conda create -y -n <CONDA_NAME>
 190 | $ conda activate <CONDA_NAME>
 191 | $ call "C:\Program Files\Microsoft Visual Studio\<VERSION>\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
 192 | ```
 193 | 
 194 | A conda environment is not required.  You can also do a PyTorch build in a
 195 | standard virtual environment, e.g., created with tools like `uv`, provided
 196 | your system has installed all the necessary dependencies unavailable as pip
 197 | packages (e.g., CUDA, MKL.)
 198 | 
 199 | ##### NVIDIA CUDA Support
 200 | If you want to compile with CUDA support, [select a supported version of CUDA from our support matrix](https://pytorch.org/get-started/locally/), then install the following:
 201 | - [NVIDIA CUDA](https://developer.nvidia.com/cuda-downloads)
 202 | - [NVIDIA cuDNN](https://developer.nvidia.com/cudnn) v9.0 or above
 203 | - [Compiler](https://gist.github.com/ax3l/9489132) compatible with CUDA
 204 | 
 205 | Note: You could refer to the [cuDNN Support Matrix](https://docs.nvidia.com/deeplearning/cudnn/backend/latest/reference/support-matrix.html) for cuDNN versions with the various supported CUDA, CUDA driver, and NVIDIA hardware.
 206 | 
 207 | If you want to disable CUDA support, export the environment variable `USE_CUDA=0`.
 208 | Other potentially useful environment variables may be found in `setup.py`.  If
 209 | CUDA is installed in a non-standard location, set PATH so that the nvcc you
 210 | want to use can be found (e.g., `export PATH=/usr/local/cuda-12.8/bin:$PATH`).
 211 | 
 212 | If you are building for NVIDIA's Jetson platforms (Jetson Nano, TX1, TX2, AGX Xavier), Instructions to install PyTorch for Jetson Nano are [available here](https://devtalk.nvidia.com/default/topic/1049071/jetson-nano/pytorch-for-jetson-nano/)
 213 | 
 214 | ##### AMD ROCm Support
 215 | If you want to compile with ROCm support, install
 216 | - [AMD ROCm](https://rocm.docs.amd.com/en/latest/deploy/linux/quick_start.html) 4.0 and above installation
 217 | - ROCm is currently supported only for Linux systems.
 218 | 
 219 | By default the build system expects ROCm to be installed in `/opt/rocm`. If ROCm is installed in a different directory, the `ROCM_PATH` environment variable must be set to the ROCm installation directory. The build system automatically detects the AMD GPU architecture. Optionally, the AMD GPU architecture can be explicitly set with the `PYTORCH_ROCM_ARCH` environment variable [AMD GPU architecture](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html#supported-gpus)
 220 | 
 221 | If you want to disable ROCm support, export the environment variable `USE_ROCM=0`.
 222 | Other potentially useful environment variables may be found in `setup.py`.
 223 | 
 224 | ##### Intel GPU Support
 225 | If you want to compile with Intel GPU support, follow these
 226 | - [PyTorch Prerequisites for Intel GPUs](https://www.intel.com/content/www/us/en/developer/articles/tool/pytorch-prerequisites-for-intel-gpu.html) instructions.
 227 | - Intel GPU is supported for Linux and Windows.
 228 | 
 229 | If you want to disable Intel GPU support, export the environment variable `USE_XPU=0`.
 230 | Other potentially useful environment variables may be found in `setup.py`.
 231 | 
 232 | #### Get the PyTorch Source
 233 | 
 234 | ```bash
 235 | git clone https://github.com/pytorch/pytorch
 236 | cd pytorch
 237 | # if you are updating an existing checkout
 238 | git submodule sync
 239 | git submodule update --init --recursive
 240 | ```
 241 | 
 242 | #### Install Dependencies
 243 | 
 244 | **Common**
 245 | 
 246 | ```bash
 247 | # Run this command from the PyTorch directory after cloning the source code using the “Get the PyTorch Source“ section above
 248 | pip install --group dev
 249 | ```
 250 | 
 251 | **On Linux**
 252 | 
 253 | ```bash
 254 | pip install mkl-static mkl-include
 255 | # CUDA only: Add LAPACK support for the GPU if needed
 256 | # magma installation: run with active conda environment. specify CUDA version to install
 257 | .ci/docker/common/install_magma_conda.sh 12.4
 258 | 
 259 | # (optional) If using torch.compile with inductor/triton, install the matching version of triton
 260 | # Run from the pytorch directory after cloning
 261 | # For Intel GPU support, please explicitly `export USE_XPU=1` before running command.
 262 | make triton
 263 | ```
 264 | 
 265 | **On Windows**
 266 | 
 267 | ```bash
 268 | pip install mkl-static mkl-include
 269 | # Add these packages if torch.distributed is needed.
 270 | # Distributed package support on Windows is a prototype feature and is subject to changes.
 271 | conda install -c conda-forge libuv=1.51
 272 | ```
 273 | 
 274 | #### Install PyTorch
 275 | 
 276 | **On Linux**
 277 | 
 278 | If you're compiling for AMD ROCm then first run this command:
 279 | 
 280 | ```bash
 281 | # Only run this if you're compiling for ROCm
 282 | python tools/amd_build/build_amd.py
 283 | ```
 284 | 
 285 | Install PyTorch
 286 | 
 287 | ```bash
 288 | # the CMake prefix for conda environment
 289 | export CMAKE_PREFIX_PATH="${CONDA_PREFIX:-'$(dirname $(which conda))/../'}:${CMAKE_PREFIX_PATH}"
 290 | python -m pip install --no-build-isolation -v -e .
 291 | 
 292 | # the CMake prefix for non-conda environment, e.g. Python venv
 293 | # call following after activating the venv
 294 | export CMAKE_PREFIX_PATH="${VIRTUAL_ENV}:${CMAKE_PREFIX_PATH}"
 295 | ```
 296 | 
 297 | **On macOS**
 298 | 
 299 | ```bash
 300 | python -m pip install --no-build-isolation -v -e .
 301 | ```
 302 | 
 303 | **On Windows**
 304 | 
 305 | If you want to build legacy python code, please refer to [Building on legacy code and CUDA](https://github.com/pytorch/pytorch/blob/main/CONTRIBUTING.md#building-on-legacy-code-and-cuda)
 306 | 
 307 | **CPU-only builds**
 308 | 
 309 | In this mode PyTorch computations will run on your CPU, not your GPU.
 310 | 
 311 | ```cmd
 312 | python -m pip install --no-build-isolation -v -e .
 313 | ```
 314 | 
 315 | Note on OpenMP: The desired OpenMP implementation is Intel OpenMP (iomp). In order to link against iomp, you'll need to manually download the library and set up the building environment by tweaking `CMAKE_INCLUDE_PATH` and `LIB`. The instruction [here](https://github.com/pytorch/pytorch/blob/main/docs/source/notes/windows.rst#building-from-source) is an example for setting up both MKL and Intel OpenMP. Without these configurations for CMake, Microsoft Visual C OpenMP runtime (vcomp) will be used.
 316 | 
 317 | **CUDA based build**
 318 | 
 319 | In this mode PyTorch computations will leverage your GPU via CUDA for faster number crunching
 320 | 
 321 | [NVTX](https://docs.nvidia.com/gameworks/content/gameworkslibrary/nvtx/nvidia_tools_extension_library_nvtx.htm) is needed to build PyTorch with CUDA.
 322 | NVTX is a part of CUDA distributive, where it is called "Nsight Compute". To install it onto an already installed CUDA run CUDA installation once again and check the corresponding checkbox.
 323 | Make sure that CUDA with Nsight Compute is installed after Visual Studio.
 324 | 
 325 | Currently, VS 2017 / 2019, and Ninja are supported as the generator of CMake. If `ninja.exe` is detected in `PATH`, then Ninja will be used as the default generator, otherwise, it will use VS 2017 / 2019.
 326 | <br/> If Ninja is selected as the generator, the latest MSVC will get selected as the underlying toolchain.
 327 | 
 328 | Additional libraries such as
 329 | [Magma](https://developer.nvidia.com/magma), [oneDNN, a.k.a. MKLDNN or DNNL](https://github.com/oneapi-src/oneDNN), and [Sccache](https://github.com/mozilla/sccache) are often needed. Please refer to the [installation-helper](https://github.com/pytorch/pytorch/tree/main/.ci/pytorch/win-test-helpers/installation-helpers) to install them.
 330 | 
 331 | You can refer to the [build_pytorch.bat](https://github.com/pytorch/pytorch/blob/main/.ci/pytorch/win-test-helpers/build_pytorch.bat) script for some other environment variables configurations
 332 | 
 333 | ```cmd
 334 | cmd
 335 | 
 336 | :: Set the environment variables after you have downloaded and unzipped the mkl package,
 337 | :: else CMake would throw an error as `Could NOT find OpenMP`.
 338 | set CMAKE_INCLUDE_PATH={Your directory}\mkl\include
 339 | set LIB={Your directory}\mkl\lib;%LIB%
 340 | 
 341 | :: Read the content in the previous section carefully before you proceed.
 342 | :: [Optional] If you want to override the underlying toolset used by Ninja and Visual Studio with CUDA, please run the following script block.
 343 | :: "Visual Studio 2019 Developer Command Prompt" will be run automatically.
 344 | :: Make sure you have CMake >= 3.12 before you do this when you use the Visual Studio generator.
 345 | set CMAKE_GENERATOR_TOOLSET_VERSION=14.27
 346 | set DISTUTILS_USE_SDK=1
 347 | for /f "usebackq tokens=*" %i in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -version [15^,17^) -products * -latest -property installationPath`) do call "%i\VC\Auxiliary\Build\vcvarsall.bat" x64 -vcvars_ver=%CMAKE_GENERATOR_TOOLSET_VERSION%
 348 | 
 349 | :: [Optional] If you want to override the CUDA host compiler
 350 | set CUDAHOSTCXX=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.27.29110\bin\HostX64\x64\cl.exe
 351 | 
 352 | python -m pip install --no-build-isolation -v -e .
 353 | ```
 354 | 
 355 | **Intel GPU builds**
 356 | 
 357 | In this mode PyTorch with Intel GPU support will be built.
 358 | 
 359 | Please make sure [the common prerequisites](#prerequisites) as well as [the prerequisites for Intel GPU](#intel-gpu-support) are properly installed and the environment variables are configured prior to starting the build. For build tool support, `Visual Studio 2022` is required.
 360 | 
 361 | Then PyTorch can be built with the command:
 362 | 
 363 | ```cmd
 364 | :: CMD Commands:
 365 | :: Set the CMAKE_PREFIX_PATH to help find corresponding packages
 366 | :: %CONDA_PREFIX% only works after `conda activate custom_env`
 367 | 
 368 | if defined CMAKE_PREFIX_PATH (
 369 |     set "CMAKE_PREFIX_PATH=%CONDA_PREFIX%\Library;%CMAKE_PREFIX_PATH%"
 370 | ) else (
 371 |     set "CMAKE_PREFIX_PATH=%CONDA_PREFIX%\Library"
 372 | )
 373 | 
 374 | python -m pip install --no-build-isolation -v -e .
 375 | ```
 376 | 
 377 | ##### Adjust Build Options (Optional)
 378 | 
 379 | You can adjust the configuration of cmake variables optionally (without building first), by doing
 380 | the following. For example, adjusting the pre-detected directories for CuDNN or BLAS can be done
 381 | with such a step.
 382 | 
 383 | On Linux
 384 | 
 385 | ```bash
 386 | export CMAKE_PREFIX_PATH="${CONDA_PREFIX:-'$(dirname $(which conda))/../'}:${CMAKE_PREFIX_PATH}"
 387 | CMAKE_ONLY=1 python setup.py build
 388 | ccmake build  # or cmake-gui build
 389 | ```
 390 | 
 391 | On macOS
 392 | 
 393 | ```bash
 394 | export CMAKE_PREFIX_PATH="${CONDA_PREFIX:-'$(dirname $(which conda))/../'}:${CMAKE_PREFIX_PATH}"
 395 | MACOSX_DEPLOYMENT_TARGET=11.0 CMAKE_ONLY=1 python setup.py build
 396 | ccmake build  # or cmake-gui build
 397 | ```
 398 | 
 399 | ### Docker Image
 400 | 
 401 | #### Using pre-built images
 402 | 
 403 | You can also pull a pre-built docker image from Docker Hub and run with docker v23.0+
 404 | 
 405 | ```bash
 406 | docker run --gpus all --rm -ti --ipc=host pytorch/pytorch:latest
 407 | ```
 408 | 
 409 | Please note that PyTorch uses shared memory to share data between processes, so if torch multiprocessing is used (e.g.
 410 | for multithreaded data loaders) the default shared memory segment size that container runs with is not enough, and you
 411 | should increase shared memory size either with `--ipc=host` or `--shm-size` command line options to `nvidia-docker run`.
 412 | 
 413 | #### Building the image yourself
 414 | 
 415 | **NOTE:** Must be built with a Docker version >= 23.0
 416 | 
 417 | The Dockerfile is supplied to build images with CUDA 12.1 support and cuDNN v9.
 418 | You can pass `PYTHON_VERSION=x.y` make variable to specify which Python version is to be used by Miniconda, or leave it
 419 | unset to use the default, as the Dockerfile uses system Python.
 420 | 
 421 | ```bash
 422 | make -f docker.Makefile
 423 | # images are tagged as docker.io/${your_docker_username}/pytorch
 424 | ```
 425 | 
 426 | You can also pass the `CMAKE_VARS="..."` environment variable to specify additional CMake variables to be passed to CMake during the build.
 427 | See [setup.py](./setup.py) for the list of available variables.
 428 | 
 429 | ```bash
 430 | make -f docker.Makefile
 431 | ```
 432 | 
 433 | ### Building the Documentation
 434 | 
 435 | To build documentation in various formats, you will need [Sphinx](http://www.sphinx-doc.org)
 436 | and the `pytorch_sphinx_theme2`.
 437 | 
 438 | Before you build the documentation locally, ensure `torch` is
 439 | installed in your environment. For small fixes, you can install the
 440 | nightly version as described in [Getting Started](https://pytorch.org/get-started/locally/).
 441 | 
 442 | For more complex fixes, such as adding a new module and docstrings for
 443 | the new module, you might need to install torch [from source](#from-source).
 444 | See [Docstring Guidelines](https://github.com/pytorch/pytorch/wiki/Docstring-Guidelines)
 445 | for docstring conventions.
 446 | 
 447 | ```bash
 448 | cd docs/
 449 | pip install -r requirements.txt
 450 | make html
 451 | make serve
 452 | ```
 453 | 
 454 | Run `make` to get a list of all available output formats.
 455 | 
 456 | If you get a katex error run `npm install katex`.  If it persists, try
 457 | `npm install -g katex`
 458 | 
 459 | > [!NOTE]
 460 | > If you see a numpy incompatibility error, run:
 461 | > ```
 462 | > pip install 'numpy<2'
 463 | > ```
 464 | 
 465 | 
 466 | #### Troubleshooting CI Errors
 467 | Your build may show errors you didn't have locally - here's how to find the errors relevant to the docs.
 468 | 
 469 | If the build has any errors, you will see something like this on the PR:
 470 | 
 471 | <img width="781" height="400" alt="Monosnap Update installation instructions for doc build · Pull Request #169534 · pytorch:pytorch 2025-12-18 18-22-53" src="https://github.com/user-attachments/assets/49a3dfe7-81c2-4246-852b-bc3f807e95af" />
 472 | 
 473 | Any doc-related errors will occur in jobs that include "doc" somewhere in the title. It doesn't look like any of these jobs are relevant to our docs.
 474 | 
 475 | 
 476 | Let's take a look anyway. Click on the job to see the logs:
 477 | 
 478 | <img width="1187" height="668" alt="Monosnap Update installation instructions for doc build · pytorch:pytorch@7380336 2025-12-18 18-24-15" src="https://github.com/user-attachments/assets/117df543-8356-4323-8e1c-ef02a95554ba" />
 479 | 
 480 | And we can be sure that this job does not involve docs.
 481 | 
 482 | Looking at this build, we can see these jobs are relevant to our docs - and they didn't have any errors:
 483 | 
 484 | <img width="777" height="395" alt="Check the docs jobs" src="https://github.com/user-attachments/assets/5d7c196b-2d40-49ad-87e3-f57de6e14a5b" />
 485 | 
 486 | You might also see a comment on the PR like this:
 487 | 
 488 | <img width="651" height="246" alt="PR Comment" src="https://github.com/user-attachments/assets/27e0120a-ba33-4b1c-b4a5-bf3064520586" />
 489 | 
 490 | We can see that some of these issues are relevant to our docs.
 491 | 
 492 | Open the logs by clicking on the `gh` link:
 493 | 
 494 | <img width="873" height="360" alt="View Logs" src="https://github.com/user-attachments/assets/ab5b862f-8026-489c-b95e-a6cd4257e4b7" />
 495 | 
 496 | And here we can see there is a doc-related error:
 497 | 
 498 | <img width="1117" height="433" alt="Doc Error" src="https://github.com/user-attachments/assets/0a275921-736d-43a7-ab0f-3e8854d43280" />
 499 | 
 500 | You can always find the relevant doc builds by going to the `Checks` tab on your PR, and scrolling down to `pull`.
 501 | 
 502 | <img width="481" height="561" alt="checks" src="https://github.com/user-attachments/assets/eef18f2b-7134-4e2e-bd90-bcdc12800132" />
 503 | 
 504 | You can either click through or toggle the accordion to see all of the jobs here, where you can see the docs jobs highlighted:
 505 | 
 506 | <img width="570" height="611" alt="jobs" src="https://github.com/user-attachments/assets/f62812ca-caee-421b-863c-54f38fd28d46" />
 507 | 
 508 | If you click through, you'll see the doc jobs at the bottom, like this:
 509 | 
 510 | <img width="354" height="312" alt="View Docs jobs" src="https://github.com/user-attachments/assets/8fadb935-5314-4c4b-a1b5-133781754f03" />
 511 | 
 512 | 
 513 | #### Building a PDF
 514 | 
 515 | To compile a PDF of all PyTorch documentation, ensure you have
 516 | `texlive` and LaTeX installed. On macOS, you can install them using:
 517 | 
 518 | ```
 519 | brew install --cask mactex
 520 | ```
 521 | 
 522 | To create the PDF:
 523 | 
 524 | 1. Run:
 525 | 
 526 |    ```
 527 |    make latexpdf
 528 |    ```
 529 | 
 530 |    This will generate the necessary files in the `build/latex` directory.
 531 | 
 532 | 2. Navigate to this directory and execute:
 533 | 
 534 |    ```
 535 |    make LATEXOPTS="-interaction=nonstopmode"
 536 |    ```
 537 | 
 538 |    This will produce a `pytorch.pdf` with the desired content. Run this
 539 |    command one more time so that it generates the correct table
 540 |    of contents and index.
 541 | 
 542 | > [!NOTE]
 543 | > To view the Table of Contents, switch to the **Table of Contents**
 544 | > view in your PDF viewer.
 545 | 
 546 | 
 547 | ### Previous Versions
 548 | 
 549 | Installation instructions and binaries for previous PyTorch versions may be found
 550 | on [our website](https://pytorch.org/get-started/previous-versions).
 551 | 
 552 | 
 553 | ## Getting Started
 554 | 
 555 | Pointers to get you started:
 556 | - [Tutorials: get you started with understanding and using PyTorch](https://pytorch.org/tutorials/)
 557 | - [Examples: easy to understand PyTorch code across all domains](https://github.com/pytorch/examples)
 558 | - [The API Reference](https://pytorch.org/docs/)
 559 | - [Glossary](https://github.com/pytorch/pytorch/blob/main/GLOSSARY.md)
 560 | 
 561 | ## Resources
 562 | 
 563 | * [PyTorch.org](https://pytorch.org/)
 564 | * [PyTorch Tutorials](https://pytorch.org/tutorials/)
 565 | * [PyTorch Examples](https://github.com/pytorch/examples)
 566 | * [PyTorch Models](https://pytorch.org/hub/)
 567 | * [Intro to Deep Learning with PyTorch from Udacity](https://www.udacity.com/course/deep-learning-pytorch--ud188)
 568 | * [Intro to Machine Learning with PyTorch from Udacity](https://www.udacity.com/course/intro-to-machine-learning-nanodegree--nd229)
 569 | * [Deep Neural Networks with PyTorch from Coursera](https://www.coursera.org/learn/deep-neural-networks-with-pytorch)
 570 | * [PyTorch Twitter](https://twitter.com/PyTorch)
 571 | * [PyTorch Blog](https://pytorch.org/blog/)
 572 | * [PyTorch YouTube](https://www.youtube.com/channel/UCWXI5YeOsh03QvJ59PMaXFw)
 573 | 
 574 | ## Communication
 575 | * Forums: Discuss implementations, research, etc. https://discuss.pytorch.org
 576 | * GitHub Issues: Bug reports, feature requests, install issues, RFCs, thoughts, etc.
 577 | * Slack: The [PyTorch Slack](https://pytorch.slack.com/) hosts a primary audience of moderate to experienced PyTorch users and developers for general chat, online discussions, collaboration, etc. If you are a beginner looking for help, the primary medium is [PyTorch Forums](https://discuss.pytorch.org). If you need a slack invite, please fill this form: https://goo.gl/forms/PP1AGvNHpSaJP8to1
 578 | * Newsletter: No-noise, a one-way email newsletter with important announcements about PyTorch. You can sign-up here: https://eepurl.com/cbG0rv
 579 | * Facebook Page: Important announcements about PyTorch. https://www.facebook.com/pytorch
 580 | * For brand guidelines, please visit our website at [pytorch.org](https://pytorch.org/)
 581 | 
 582 | ## Releases and Contributing
 583 | 
 584 | Typically, PyTorch has three minor releases a year. Please let us know if you encounter a bug by [filing an issue](https://github.com/pytorch/pytorch/issues).
 585 | 
 586 | We appreciate all contributions. If you are planning to contribute back bug-fixes, please do so without any further discussion.
 587 | 
 588 | If you plan to contribute new features, utility functions, or extensions to the core, please first open an issue and discuss the feature with us.
 589 | Sending a PR without discussion might end up resulting in a rejected PR because we might be taking the core in a different direction than you might be aware of.
 590 | 
 591 | To learn more about making a contribution to PyTorch, please see our [Contribution page](CONTRIBUTING.md). For more information about PyTorch releases, see [Release page](RELEASE.md).
 592 | 
 593 | ## The Team
 594 | 
 595 | PyTorch is a community-driven project with several skillful engineers and researchers contributing to it.
 596 | 
 597 | PyTorch is currently maintained by [Soumith Chintala](http://soumith.ch), [Gregory Chanan](https://github.com/gchanan), [Dmytro Dzhulgakov](https://github.com/dzhulgakov), [Edward Yang](https://github.com/ezyang), [Alban Desmaison](https://github.com/albanD), [Piotr Bialecki](https://github.com/ptrblck) and [Nikita Shulga](https://github.com/malfet) with major contributions coming from hundreds of talented individuals in various forms and means.
 598 | A non-exhaustive but growing list needs to mention: [Trevor Killeen](https://github.com/killeent), [Sasank Chilamkurthy](https://github.com/chsasank), [Sergey Zagoruyko](https://github.com/szagoruyko), [Adam Lerer](https://github.com/adamlerer), [Francisco Massa](https://github.com/fmassa), [Alykhan Tejani](https://github.com/alykhantejani), [Luca Antiga](https://github.com/lantiga), [Alban Desmaison](https://github.com/albanD), [Andreas Koepf](https://github.com/andreaskoepf), [James Bradbury](https://github.com/jekbradbury), [Zeming Lin](https://github.com/ebetica), [Yuandong Tian](https://github.com/yuandong-tian), [Guillaume Lample](https://github.com/glample), [Marat Dukhan](https://github.com/Maratyszcza), [Natalia Gimelshein](https://github.com/ngimel), [Christian Sarofeen](https://github.com/csarofeen), [Martin Raison](https://github.com/martinraison), [Edward Yang](https://github.com/ezyang), [Zachary Devito](https://github.com/zdevito). <!-- codespell:ignore -->
 599 | 
 600 | Note: This project is unrelated to [hughperkins/pytorch](https://github.com/hughperkins/pytorch) with the same name. Hugh is a valuable contributor to the Torch community and has helped with many things Torch and PyTorch.
 601 | 
 602 | ## License
 603 | 
 604 | PyTorch has a BSD-style license, as found in the [LICENSE](LICENSE) file.
```


---
## torch/_dynamo/CLAUDE.md

```
   1 | # torch/_dynamo
   2 | 
   3 | TorchDynamo is a Python-level JIT compiler that captures PyTorch programs into
   4 | FX graphs by symbolically executing Python bytecode. It hooks into CPython's
   5 | PEP 523 frame evaluation API to intercept execution, traces operations into an
   6 | FX graph, compiles the graph with a backend (e.g. Inductor), and generates new
   7 | bytecode that calls the compiled code.
   8 | 
   9 | ## Architecture Overview
  10 | 
  11 | The compilation pipeline, in execution order:
  12 | 
  13 | 1. **`eval_frame.py`** — Runtime entry point. `torch.compile()` wraps a
  14 |    function in an `OptimizedModule`. At runtime, the C extension
  15 |    (`torch._C._dynamo.eval_frame`) intercepts Python frames via PEP 523.
  16 | 2. **`convert_frame.py`** — `ConvertFrameAssert.__call__` checks caches,
  17 |    handles recompilation limits, calls `_compile()` → `trace_frame()`.
  18 | 3. **`symbolic_convert.py`** — The heart of Dynamo. `InstructionTranslator`
  19 |    symbolically executes bytecode instruction-by-instruction. Maintains a
  20 |    symbolic `stack` (list of `VariableTracker`s) and `symbolic_locals` (dict of
  21 |    name → `VariableTracker`). Opcodes are dispatched via a `dispatch_table`
  22 |    built by `BytecodeDispatchTableMeta`.
  23 | 4. **`output_graph.py`** — `OutputGraph` owns the FX graph being built (via
  24 |    `SubgraphTracer`), the `SideEffects` tracker, guards, shape environment,
  25 |    and graph args. `compile_subgraph()` finalizes the graph, calls the backend,
  26 |    and generates output bytecode.
  27 | 5. **`codegen.py`** — `PyCodegen` emits output bytecode: loads graph inputs
  28 |    (via `Source.reconstruct()`), calls the compiled graph, unpacks outputs, and
  29 |    replays side effects.
  30 | 6. **`resume_execution.py`** — Generates continuation functions for execution
  31 |    after graph breaks.
  32 | 
  33 | ## Key Abstractions
  34 | 
  35 | ### VariableTracker (`variables/`)
  36 | 
  37 | Every Python value encountered during tracing is wrapped in a `VariableTracker`
  38 | subclass. Key interface: `as_python_constant()`, `as_proxy()`,
  39 | `call_function()`, `call_method()`, `var_getattr()`, `reconstruct()`.
  40 | 
  41 | Key fields: `source` (where the value came from, for guards) and
  42 | `mutation_type` (whether/how mutations are tracked).
  43 | 
  44 | **Factory**: `VariableTracker.build(tx, value, source=...)` dispatches to
  45 | `VariableBuilder` (sourced values needing guards) or `SourcelessBuilder`
  46 | (values created during tracing).
  47 | 
  48 | Key subclass families in `variables/`: `TensorVariable` / `SymNodeVariable`
  49 | (tensor.py), `ConstantVariable` (constant.py), `ListVariable` /
  50 | `TupleVariable` (lists.py), `ConstDictVariable` / `SetVariable` (dicts.py),
  51 | `UserFunctionVariable` (functions.py), `BuiltinVariable` (builtin.py),
  52 | `NNModuleVariable` (nn_module.py), `UserDefinedObjectVariable`
  53 | (user_defined.py), `TorchHigherOrderOperatorVariable` (higher_order_ops.py),
  54 | `LazyVariableTracker` (lazy.py). `VariableBuilder` and `SourcelessBuilder` are
  55 | in builder.py.
  56 | 
  57 | ### Source (`source.py`)
  58 | 
  59 | Tracks value provenance — how to access a value at runtime. Used for guard
  60 | generation (`source.make_guard(GuardBuilder.XXX)`) and bytecode reconstruction
  61 | (`source.reconstruct(codegen)`). Root sources: `LocalSource`, `GlobalSource`.
  62 | Chained sources: `AttrSource`, `GetItemSource`, `NNModuleSource`, etc.
  63 | 
  64 | ### Guards (`guards.py`)
  65 | 
  66 | Runtime conditions that must hold for cached compiled code to be reused.
  67 | Install via `install_guard(source.make_guard(GuardBuilder.TYPE_MATCH))`.
  68 | Common types: `TYPE_MATCH`, `ID_MATCH`, `EQUALS_MATCH`, `TENSOR_MATCH`,
  69 | `SEQUENCE_LENGTH`. At finalization, `CheckFunctionManager` builds a tree of
  70 | C++ `GuardManager` objects for fast runtime checking.
  71 | 
  72 | ### Side Effects (`side_effects.py`)
  73 | 
  74 | Tracks mutations during tracing (attribute stores, list mutations, cell
  75 | variable updates, tensor hooks) and replays them as bytecode after graph
  76 | execution. The `MutationType` system (`variables/base.py`) controls what
  77 | mutations are allowed: `ValueMutationNew/Existing`,
  78 | `AttributeMutationNew/Existing`, or `None` (immutable). The `scope` field
  79 | prevents cross-scope mutations inside higher-order operators.
  80 | 
  81 | ### Other key files
  82 | 
  83 | - `trace_rules.py` — inline/skip/graph-break decisions per function
  84 | - `exc.py` — exception hierarchy: `Unsupported` (graph break), `RestartAnalysis`
  85 |   (restart tracing), `ObservedException` (user exceptions during tracing),
  86 |   `BackendCompilerFailed`
  87 | - `config.py` — configuration flags, supports `config.patch()` context
  88 |   manager/decorator
  89 | - `bytecode_transformation.py` / `bytecode_analysis.py` — low-level bytecode
  90 |   manipulation, liveness analysis
  91 | - `pgo.py` — profile-guided optimization for dynamic shapes
  92 | - `polyfills/` — traceable replacements for stdlib functions
  93 | - `repro/` — reproduction/minification tools
  94 | 
  95 | ## Graph Breaks
  96 | 
  97 | Call `unimplemented()` (from `exc.py`) to trigger a graph break:
  98 | 
  99 | ```python
 100 | from torch._dynamo.exc import unimplemented
 101 | from torch._dynamo import graph_break_hints
 102 | 
 103 | unimplemented(
 104 |     gb_type="short_category_name",
 105 |     context=f"dynamic details: {value}",
 106 |     explanation="Human-readable explanation of why this breaks the graph.",
 107 |     hints=[*graph_break_hints.SUPPORTABLE],
 108 | )
 109 | ```
 110 | 
 111 | - `gb_type`: Context-free category (no dynamic strings).
 112 | - `context`: Developer-facing details (can be dynamic).
 113 | - `explanation`: User-facing explanation (can be dynamic).
 114 | - `hints`: Use constants from `graph_break_hints.py`: `SUPPORTABLE`,
 115 |   `FUNDAMENTAL`, `DIFFICULT`, `DYNAMO_BUG`, `USER_ERROR`,
 116 |   `CAUSED_BY_EARLIER_GRAPH_BREAK`.
 117 | 
 118 | The `break_graph_if_unsupported` decorator on instruction handlers catches
 119 | `Unsupported`, logs the graph break, updates the `SpeculationLog`, and restarts
 120 | analysis. On the second pass, the partial graph is compiled at the break point
 121 | and a resume function handles the rest.
 122 | 
 123 | ## Testing
 124 | 
 125 | Tests live in `test/dynamo/`. Use `torch._dynamo.test_case.TestCase` as base
 126 | class — it calls `torch._dynamo.reset()` in setUp/tearDown and patches config
 127 | for strict error checking.
 128 | 
 129 | ```bash
 130 | python test/dynamo/test_misc.py                       # whole file
 131 | python test/dynamo/test_misc.py MiscTests.test_foo    # single test
 132 | python test/dynamo/test_misc.py -k test_foo           # pattern match
 133 | ```
 134 | 
 135 | ### Common patterns
 136 | 
 137 | The default backend to `torch.compile()` is `backend="eager"`.
 138 | 
 139 | **CompileCounter** — count compilations and graph ops:
 140 | ```python
 141 | cnt = torch._dynamo.testing.CompileCounter()
 142 | 
 143 | @torch.compile(backend=cnt)
 144 | def fn(x):
 145 |     return x + 1
 146 | 
 147 | fn(torch.randn(10))
 148 | self.assertEqual(cnt.frame_count, 1)
 149 | self.assertEqual(cnt.op_count, 1)
 150 | ```
 151 | 
 152 | **fullgraph=True** — assert no graph breaks:
 153 | ```python
 154 | torch.compile(fn, backend="eager", fullgraph=True)(x)
 155 | ```
 156 | 
 157 | **EagerAndRecordGraphs** — inspect captured FX graphs:
 158 | ```python
 159 | backend = torch._dynamo.testing.EagerAndRecordGraphs()
 160 | torch.compile(fn, backend=backend)(x)
 161 | graph = backend.graphs[0]
 162 | ```
 163 | 
 164 | **normalize_gm + assertExpectedInline** — snapshot test graph output:
 165 | ```python
 166 | from torch._dynamo.testing import normalize_gm
 167 | self.assertExpectedInline(
 168 |     normalize_gm(backend.graphs[0].print_readable(False)),
 169 |     """\
 170 | expected output here
 171 | """,
 172 | )
 173 | ```
 174 | 
 175 | Call `torch._dynamo.reset()` within a test when testing multiple compilation
 176 | scenarios in a single test method. The base class handles setUp/tearDown reset
 177 | automatically.
 178 | 
 179 | ## Debugging
 180 | 
 181 | ### TORCH_LOGS
 182 | 
 183 | ```bash
 184 | TORCH_LOGS="graph_breaks" python script.py       # see graph breaks
 185 | TORCH_LOGS="guards,recompiles" python script.py  # see guards and recompilation reasons
 186 | TORCH_LOGS="graph_code" python script.py         # see captured FX graph code
 187 | TORCH_LOGS="+dynamo" python script.py            # full debug logging
 188 | TORCH_LOGS="bytecode" python script.py           # see bytecode transformations
 189 | ```
 190 | 
 191 | ### Structured tracing (for production)
 192 | 
 193 | ```bash
 194 | TORCH_TRACE=/path/to/dir python script.py  # explicit trace directory
 195 | ```
 196 | 
 197 | Analyze with `tlparse`.
 198 | 
 199 | ### Compile-time profiling
 200 | 
 201 | `TORCH_COMPILE_DYNAMO_PROFILER=1` prints per-function cumtime/tottime
 202 | (cProfile-style) showing where Dynamo spends time during tracing. Set to a
 203 | file path instead to save a profile loadable by `snakeviz`.
 204 | 
 205 | ### comptime.breakpoint() (`comptime.py`)
 206 | 
 207 | Drops into pdb during **compilation** to inspect Dynamo state. Call
 208 | `comptime.breakpoint()` in user code; in the pdb session use `ctx`
 209 | (`ComptimeContext`) to call `print_locals()`, `print_bt()`, `print_graph()`,
 210 | or `get_local("x").as_fake()`.
 211 | 
 212 | ### Bytecode Debugger (`bytecode_debugger.py`)
 213 | 
 214 | pdb-like debugger for stepping through Dynamo-generated bytecode. Useful for
 215 | debugging segfaults (no Python traceback) and codegen errors.
 216 | 
 217 | ```python
 218 | with torch._dynamo.bytecode_debugger.debug():
 219 |     my_compiled_fn(x)
 220 | ```
 221 | 
 222 | **Programmatic breakpoints** (no graph break): call
 223 | `torch._dynamo.bytecode_debugger.breakpoint()` in user code, or
 224 | `codegen.extend_output(create_breakpoint())` in codegen. Auto-activates
 225 | without an explicit `debug()` wrapper.
 226 | 
 227 | **Segfault debugging**: `v` (verbose) then `c` (continue) — every instruction
 228 | is printed with `flush=True` before execution, so the last line before a crash
 229 | is the culprit. On exceptions, the debugger stops at the faulting instruction
 230 | automatically.
 231 | 
 232 | ## C++ Runtime (`torch/csrc/dynamo/`)
 233 | 
 234 | The C/C++ layer implements the PEP 523 frame evaluation hook, the cache, and
 235 | the guard evaluation tree. Performance-critical runtime on every Python frame.
 236 | 
 237 | ### Frame Evaluation
 238 | 
 239 | **`eval_frame.c`** — Installs a custom frame evaluation function via
 240 | `_PyInterpreterState_SetEvalFrameFunc`. A thread-local callback controls
 241 | behavior: `None` (disabled), `Py_False` (run-only / cache lookup), or a
 242 | callable (full Dynamo).
 243 | 
 244 | **`eval_frame_cpp.cpp`** — `dynamo__custom_eval_frame` is called for every
 245 | frame: gets `ExtraState` from the code object, builds a `FrameLocalsMapping`
 246 | (O(1) access to locals without dict materialization), evaluates guards via
 247 | `run_root_guard_manager()` across all `CacheEntry`s (LRU ordered). On cache
 248 | hit, executes compiled code via a shadow frame (`dynamo_eval_custom_code_impl`
 249 | copies `localsplus` into a new frame with the compiled code object). On miss,
 250 | calls the Python callback to trigger compilation.
 251 | 
 252 | ### Cache
 253 | 
 254 | **`extra_state.cpp/.h`** — `ExtraState` is attached per code object via
 255 | `_PyCode_SetExtra`. Contains a `cache_entry_list` (LRU linked list),
 256 | `frame_state` (dynamic shapes detection), and `FrameExecStrategy`.
 257 | 
 258 | **`cache_entry.cpp/.h`** — Each `CacheEntry` stores a `RootGuardManager*`
 259 | (raw C++ pointer for fast guard eval), the compiled code object, and the
 260 | backend.
 261 | 
 262 | ### Guard Evaluation Tree (`guards.cpp`)
 263 | 
 264 | Guards are organized as a C++ tree (~7800 lines) mirroring the data access
 265 | pattern. `RootGuardManager` is the root, receiving a `FrameLocalsMapping`.
 266 | Each `GuardManager` node has leaf guards and child accessors.
 267 | 
 268 | **LeafGuard** subclasses: `TYPE_MATCH` (Py_TYPE pointer comparison),
 269 | `ID_MATCH`, `EQUALS_MATCH`, `TENSOR_MATCH` (dtype/device/shape/strides/dispatch
 270 | keys in C++), `DICT_VERSION`, `GLOBAL_STATE` (grad mode, autocast, etc.).
 271 | 
 272 | **GuardAccessor** subclasses define tree edges: `FrameLocalsGuardAccessor`
 273 | (O(1) index), `GetAttrGuardAccessor`, `DictGetItemGuardAccessor`,
 274 | `GlobalsGuardAccessor`, etc.
 275 | 
 276 | Key optimizations: fail-fast accessor reordering, dict version tag matching to
 277 | skip subtrees, `FrameLocalsMapping` avoids dict construction,
 278 | `check_nopybind()` avoids pybind11 overhead.
 279 | 
 280 | ### Other C++ files
 281 | 
 282 | - `framelocals_mapping.cpp` — O(1) frame locals/cells/freevars access
 283 | - `cpython_defs.c` — copied CPython internals for frame manipulation
 284 | - `init.cpp` — `torch._C._dynamo` module and pybind11 bindings
 285 | - `debug_macros.h` — `DEBUG_TRACE`, `NULL_CHECK`, `INSPECT(...)` (drops into
 286 |   pdb from C)
 287 | - `compiled_autograd.cpp/.h` — compiled autograd engine
```
