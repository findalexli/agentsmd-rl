# Agent Config Files for pytorch-hip-stream-masquerading-include

Repo: pytorch/pytorch
Commit: 4b8a514606230b60bb8f27be5f11612f21b4aec1
Files found: 32


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
  10 | ## First Step: Always Check Device and Shape Matching
  11 | 
  12 | **For ANY AOTI error (segfault, exception, crash, wrong output), ALWAYS check these first:**
  13 | 
  14 | 1. **Compile device == Load device**: The model must be loaded on the same device type it was compiled on
  15 | 2. **Input devices match**: Runtime inputs must be on the same device as the compiled model
  16 | 3. **Input shapes match**: Runtime input shapes must match the shapes used during compilation (or satisfy dynamic shape constraints)
  17 | 
  18 | ```python
  19 | # During compilation - note the device and shapes
  20 | model = MyModel().eval()           # What device? CPU or .cuda()?
  21 | inp = torch.randn(2, 10)           # What device? What shape?
  22 | compiled_so = torch._inductor.aot_compile(model, (inp,))
  23 | 
  24 | # During loading - device type MUST match compilation
  25 | loaded = torch._export.aot_load(compiled_so, "???")  # Must match model/input device above
  26 | 
  27 | # During inference - device and shapes MUST match
  28 | out = loaded(inp.to("???"))  # Must match compile device, shape must match
  29 | ```
  30 | 
  31 | **If any of these don't match, you will get errors ranging from segfaults to exceptions to wrong outputs.**
  32 | 
  33 | ## Key Constraint: Device Type Matching
  34 | 
  35 | **AOTI requires compile and load to use the same device type.**
  36 | 
  37 | - If you compile on CUDA, you must load on CUDA (device index can differ)
  38 | - If you compile on CPU, you must load on CPU
  39 | - Cross-device loading (e.g., compile on GPU, load on CPU) is NOT supported
  40 | 
  41 | ## Common Error Patterns
  42 | 
  43 | ### 1. Device Mismatch Segfault
  44 | 
  45 | **Symptom**: Segfault, exception, or crash during `aot_load()` or model execution.
  46 | 
  47 | **Example error messages**:
  48 | - `The specified pointer resides on host memory and is not registered with any CUDA device`
  49 | - Crash during constant loading in AOTInductorModelBase
  50 | - `Expected out tensor to have device cuda:0, but got cpu instead`
  51 | 
  52 | **Cause**: Compile and load device types don't match (see "First Step" above).
  53 | 
  54 | **Solution**: Ensure compile and load use the same device type. If compiled on CPU, load on CPU. If compiled on CUDA, load on CUDA.
  55 | 
  56 | ### 2. Input Device Mismatch at Runtime
  57 | 
  58 | **Symptom**: RuntimeError during model execution.
  59 | 
  60 | **Cause**: Input device doesn't match compile device (see "First Step" above).
  61 | 
  62 | **Better Debugging**: Run with `AOTI_RUNTIME_CHECK_INPUTS=1` for clearer errors. This flag validates all input properties including device type, dtype, sizes, and strides:
  63 | ```bash
  64 | AOTI_RUNTIME_CHECK_INPUTS=1 python your_script.py
  65 | ```
  66 | 
  67 | This produces actionable error messages like:
  68 | ```
  69 | Error: input_handles[0]: unmatched device type, expected: 0(cpu), but got: 1(cuda)
  70 | ```
  71 | 
  72 | 
  73 | ## Debugging CUDA Illegal Memory Access (IMA) Errors
  74 | 
  75 | If you encounter CUDA illegal memory access errors, follow this systematic approach:
  76 | 
  77 | ### Step 1: Sanity Checks
  78 | 
  79 | Before diving deep, try these debugging flags:
  80 | 
  81 | ```bash
  82 | AOTI_RUNTIME_CHECK_INPUTS=1
  83 | TORCHINDUCTOR_NAN_ASSERTS=1
  84 | ```
  85 | 
  86 | These flags take effect at compilation time (at codegen time):
  87 | 
  88 | - `AOTI_RUNTIME_CHECK_INPUTS=1` checks if inputs satisfy the same guards used during compilation
  89 | - `TORCHINDUCTOR_NAN_ASSERTS=1` adds codegen before and after each kernel to check for NaN
  90 | 
  91 | ### Step 2: Pinpoint the CUDA IMA
  92 | 
  93 | CUDA IMA errors can be non-deterministic. Use these flags to trigger the error deterministically:
  94 | 
  95 | ```bash
  96 | PYTORCH_NO_CUDA_MEMORY_CACHING=1
  97 | CUDA_LAUNCH_BLOCKING=1
  98 | ```
  99 | 
 100 | These flags take effect at runtime:
 101 | 
 102 | - `PYTORCH_NO_CUDA_MEMORY_CACHING=1` disables PyTorch's Caching Allocator, which allocates bigger buffers than needed immediately. This is usually why CUDA IMA errors are non-deterministic.
 103 | - `CUDA_LAUNCH_BLOCKING=1` forces kernels to launch one at a time. Without this, you get "CUDA kernel errors might be asynchronously reported" warnings since kernels launch asynchronously.
 104 | 
 105 | ### Step 3: Identify Problematic Kernels with Intermediate Value Debugger
 106 | 
 107 | Use the AOTI Intermediate Value Debugger to pinpoint the problematic kernel:
 108 | 
 109 | ```bash
 110 | AOT_INDUCTOR_DEBUG_INTERMEDIATE_VALUE_PRINTER=3
 111 | ```
 112 | 
 113 | This prints kernels one by one at runtime. Together with previous flags, this shows which kernel was launched right before the error.
 114 | 
 115 | To inspect inputs to a specific kernel:
 116 | 
 117 | ```bash
 118 | AOT_INDUCTOR_FILTERED_KERNELS_TO_PRINT="triton_poi_fused_add_ge_logical_and_logical_or_lt_231,_add_position_embeddings_kernel_5" AOT_INDUCTOR_DEBUG_INTERMEDIATE_VALUE_PRINTER=2
 119 | ```
 120 | 
 121 | If inputs to the kernel are unexpected, inspect the kernel that produces the bad input.
 122 | 
 123 | ## Additional Debugging Tools
 124 | 
 125 | ### Logging and Tracing
 126 | 
 127 | - **tlparse / TORCH_TRACE**: Provides complete output codes and records guards used
 128 | - **TORCH_LOGS**: Use `TORCH_LOGS="+inductor,output_code"` to see more PT2 internal logs
 129 | - **TORCH_SHOW_CPP_STACKTRACES**: Set to `1` to see more stack traces
 130 | 
 131 | ### Common Sources of Issues
 132 | 
 133 | - **Dynamic shapes**: Historically a source of many IMAs. Pay special attention when debugging dynamic shape scenarios.
 134 | - **Custom ops**: Especially when implemented in C++ with dynamic shapes. The meta function may need to be Symint'ified.
 135 | 
 136 | ## API Notes
 137 | 
 138 | ### Deprecated API
 139 | ```python
 140 | torch._export.aot_compile()  # Deprecated
 141 | torch._export.aot_load()     # Deprecated
 142 | ```
 143 | 
 144 | ### Current API
 145 | ```python
 146 | torch._inductor.aoti_compile_and_package()
 147 | torch._inductor.aoti_load_package()
 148 | ```
 149 | 
 150 | The new API stores device metadata in the package, so `aoti_load_package()` automatically uses the correct device type. You can only change the device *index* (e.g., cuda:0 vs cuda:1), not the device *type*.
 151 | 
 152 | ## Environment Variables Summary
 153 | 
 154 | | Variable | When | Purpose |
 155 | |----------|------|---------|
 156 | | `AOTI_RUNTIME_CHECK_INPUTS=1` | Compile time | Validate inputs match compilation guards |
 157 | | `TORCHINDUCTOR_NAN_ASSERTS=1` | Compile time | Check for NaN before/after kernels |
 158 | | `PYTORCH_NO_CUDA_MEMORY_CACHING=1` | Runtime | Make IMA errors deterministic |
 159 | | `CUDA_LAUNCH_BLOCKING=1` | Runtime | Force synchronous kernel launches |
 160 | | `AOT_INDUCTOR_DEBUG_INTERMEDIATE_VALUE_PRINTER=3` | Compile time | Print kernels at runtime |
 161 | | `TORCH_LOGS="+inductor,output_code"` | Runtime | See PT2 internal logs |
 162 | | `TORCH_SHOW_CPP_STACKTRACES=1` | Runtime | Show C++ stack traces |
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
  83 | When invoked via workflow, PR data is passed as context. The PR number or diff will be available in the prompt.
  84 | 
  85 | ## Review Workflow
  86 | 
  87 | ### Step 1: Fetch PR Information
  88 | 
  89 | For local mode, use `gh` commands to get:
  90 | 1. PR metadata (title, description, author)
  91 | 2. List of changed files
  92 | 3. Full diff of changes
  93 | 4. Existing comments/reviews
  94 | 5. Fetch associated issue information when applicable
  95 | 
  96 | ### Step 2: Analyze Changes
  97 | 
  98 | Read through the diff systematically:
  99 | 1. Identify the purpose of the change from title/description/issue
 100 | 2. Group changes by type (new code, tests, config, docs)
 101 | 3. Note the scope of changes (files affected, lines changed)
 102 | 
 103 | ### Step 3: Deep Review
 104 | 
 105 | Perform thorough line-by-line analysis using the review checklist. See [review-checklist.md](review-checklist.md) for detailed criteria covering:
 106 | - Code quality and design
 107 | - Testing adequacy
 108 | - Security considerations
 109 | - Performance implications
 110 | - Any behavior change not expected by author
 111 | 
 112 | ### Step 4: Check Backward Compatibility
 113 | 
 114 | Evaluate BC implications. See [bc-guidelines.md](bc-guidelines.md) for:
 115 | - What constitutes a BC-breaking change
 116 | - Required deprecation patterns
 117 | - Common BC pitfalls
 118 | 
 119 | ### Step 5: Formulate Review
 120 | 
 121 | Structure your review with actionable feedback organized by category.
 122 | 
 123 | ## Review Areas
 124 | 
 125 | | Area | Focus | Reference |
 126 | |------|-------|-----------|
 127 | | Code Quality | Abstractions, patterns, complexity | [review-checklist.md](review-checklist.md) |
 128 | | API Design | New patterns, flag-based access, broader implications | [review-checklist.md](review-checklist.md) |
 129 | | Testing | Coverage, patterns, edge cases | [review-checklist.md](review-checklist.md) |
 130 | | Security | Injection, credentials, input handling | [review-checklist.md](review-checklist.md) |
 131 | | Performance | Regressions, device handling, memory | [review-checklist.md](review-checklist.md) |
 132 | | BC | Breaking changes, deprecation | [bc-guidelines.md](bc-guidelines.md) |
 133 | 
 134 | ## Output Format
 135 | 
 136 | Structure your review as follows:
 137 | 
 138 | ```markdown
 139 | ## PR Review: #<number>
 140 | <!-- Or for local branch reviews: -->
 141 | ## Branch Review: <branch-name> (vs main)
 142 | 
 143 | ### Summary
 144 | Brief overall assessment of the changes (1-2 sentences).
 145 | 
 146 | ### Code Quality
 147 | [Issues and suggestions, or "No concerns" if none]
 148 | 
 149 | ### API Design
 150 | [Flag new patterns, internal-access flags, or broader implications if any. Otherwise omit this section.]
 151 | 
 152 | ### Testing
 153 | - [ ] Tests exist for new functionality
 154 | - [ ] Edge cases covered
 155 | - [ ] Tests follow PyTorch patterns (TestCase, assertEqual)
 156 | [Additional testing feedback]
 157 | 
 158 | ### Security
 159 | [Issues if any, or "No security concerns identified"]
 160 | 
 161 | ### Backward Compatibility
 162 | [BC concerns if any, or "No BC-breaking changes"]
 163 | 
 164 | ### Performance
 165 | [Performance concerns if any, or "No performance concerns"]
 166 | 
 167 | ### Recommendation
 168 | **Approve** / **Request Changes** / **Needs Discussion**
 169 | 
 170 | [Brief justification for recommendation]
 171 | ```
 172 | 
 173 | ### Specific Comments (Detailed Review Only)
 174 | 
 175 | **Only include this section if the user requests a "detailed" or "in depth" review.**
 176 | 
 177 | **Do not repeat observations already made in other sections.** This section is for additional file-specific feedback that doesn't fit into the categorized sections above.
 178 | 
 179 | When requested, add file-specific feedback with line references:
 180 | 
 181 | ```markdown
 182 | ### Specific Comments
 183 | - `src/module.py:42` - Consider extracting this logic into a named function for clarity
 184 | - `test/test_feature.py:100-105` - Missing test for error case when input is None
 185 | - `torch/nn/modules/linear.py:78` - This allocation could be moved outside the loop
 186 | ```
 187 | 
 188 | ## Key Principles
 189 | 
 190 | 1. **No repetition** - Each observation appears in exactly one section. Never repeat the same issue, concern, or suggestion across multiple sections. If an issue spans categories (e.g., a security issue that also affects performance), place it in the most relevant section only.
 191 | 2. **Focus on what CI cannot check** - Don't comment on formatting, linting, or type errors
 192 | 3. **Be specific** - Reference file paths and line numbers
 193 | 4. **Be actionable** - Provide concrete suggestions, not vague concerns
 194 | 5. **Be proportionate** - Minor issues shouldn't block, but note them
 195 | 6. **Assume competence** - The author knows PyTorch; explain only non-obvious context
 196 | 
 197 | ## Files to Reference
 198 | 
 199 | When reviewing, consult these project files for context:
 200 | - `CLAUDE.md` - Coding style philosophy and testing patterns
 201 | - `CONTRIBUTING.md` - PR requirements and review process
 202 | - `torch/testing/_internal/common_utils.py` - Test patterns and utilities
 203 | - `torch/testing/_internal/opinfo/core.py` - OpInfo test framework
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
  32 | 
  33 | ### Common Issues to Flag
  34 | 
  35 | - Dynamic `setattr`/`getattr` for state management (prefer explicit class members)
  36 | - Unused imports, variables, or dead code paths
  37 | - Copy-pasted code that could be a shared helper
  38 | - Magic numbers without explanation
  39 | - Overly defensive error handling for impossible cases
  40 | 
  41 | ## Testing
  42 | 
  43 | ### Test Existence
  44 | 
  45 | - [ ] **Tests exist** - New functionality has corresponding tests
  46 | - [ ] **Tests are in the right place** - Tests should be added to an existing test file next to other related tests
  47 | - [ ] **New test file is rare** - New test file should only be added when new major features are added
  48 | 
  49 | ### Test Patterns
  50 | 
  51 | - [ ] **Use OpInfo** - Any testing for an operator or a cross cutting feature must be done via OpInfo
  52 | - [ ] **Use TestCase** - Tests inherit from `torch.testing._internal.common_utils.TestCase`
  53 | - [ ] **Use run_tests** - Test file ends with `if __name__ == "__main__": run_tests()`
  54 | - [ ] **Use assertEqual for tensors** - Tensor comparisons use `assertEqual`, not raw assertions
  55 | - [ ] **Descriptive test names** - Test method names describe what is being tested
  56 | - [ ] **Device generic** - Any test checking compute result should happen in a Device-generic test class (taking device as an argument). Device-specific test should be very rare and in device-specific test files.
  57 | 
  58 | ### Test Quality
  59 | 
  60 | - [ ] **Edge cases covered** - Tests include boundary conditions, empty inputs, error cases
  61 | - [ ] **Error conditions tested** - Expected exceptions are tested with `assertRaises` or `assertRaisesRegex`
  62 | - [ ] **No duplicated test logic** - Similar tests share a private helper method (e.g., `_test_foo(config)`) called from individual tests with different configs
  63 | 
  64 | **Example of good test structure:**
  65 | ```python
  66 | def _test_feature_with_config(self, flag, expected_shape):
  67 |     """Shared test logic called by device-specific tests."""
  68 |     x = torch.randn(10)
  69 |     result = my_feature(x, flag)
  70 |     self.assertEqual(result.shape, expected_shape)
  71 | 
  72 | def test_feature_enabled(self):
  73 |     self._test_feature_with_config(True, (10, 10))
  74 | 
  75 | def test_feature_disabled(self):
  76 |     self._test_feature_with_config(False, (10, 5))
  77 | ```
  78 | 
  79 | ### Common Testing Issues
  80 | 
  81 | - Tests that only check the happy path without error cases
  82 | - Duplicated test code that should be a parameterized helper
  83 | - Tests that don't clean up resources (files, CUDA memory)
  84 | - Flaky tests (timing-dependent, order-dependent, golden value)
  85 | - Tests that skip without clear justification
  86 | 
  87 | ## Security
  88 | 
  89 | ### CI/CD and Workflow Security
  90 | 
  91 | When reviewing changes to workflows, build scripts, or CI configuration:
  92 | 
  93 | - [ ] **No secrets in workflow files** - PyTorch does not use repo secrets mechanism due to non-ephemeral runners; secrets can be compromised via reverse shell attacks
  94 | - [ ] **Ephemeral runners for sensitive jobs** - Binary builds, uploads, and merge actions must run on ephemeral runners only
  95 | - [ ] **No cache-dependent binaries in sensitive contexts** - sccache-backed builds are susceptible to cache corruption; these artifacts should not access sensitive info or be published for general use
  96 | - [ ] **Protected branch rules respected** - Changes to merge rules, release workflows, or deployment environments require extra scrutiny
  97 | - [ ] **Immutable artifact references** - Docker images use immutable tags; no overwriting of published artifacts
  98 | 
  99 | ### PyTorch API Security
 100 | 
 101 | When reviewing changes to PyTorch APIs and user-facing code:
 102 | 
 103 | - [ ] **Model loading surfaces** - `torch.load` has a large attack surface; changes should not expand unsafe deserialization. Prefer safetensors for new serialization APIs
 104 | - [ ] **TorchScript security** - TorchScript models are executable code; introspection tools like `torch.utils.model_dump` can execute code from untrusted models and should not be used
 105 | - [ ] **Distributed primitives** - `torch.distributed`, RPC, and TCPStore have no auth/encryption and accept connections from anywhere; they are for internal networks only, not untrusted environments
 106 | - [ ] **No new pickle usage** - Avoid adding `pickle.load` or `torch.load` without `weights_only=True` on paths that could receive untrusted data
 107 | 
 108 | ## Performance
 109 | 
 110 | ### Obvious Regressions
 111 | 
 112 | - [ ] **No unnecessary allocations** - Tensors are not repeatedly created in hot loops
 113 | - [ ] **Appropriate in-place operations** - Use in-place ops where possible in performance-critical paths
 114 | - [ ] **No Python loops over tensors** - Prefer vectorized operations over iterating tensor elements
 115 | 
 116 | ### Device Handling
 117 | 
 118 | - [ ] **Device consistency** - Operations don't unexpectedly move tensors between devices
 119 | - [ ] **CUDA considerations** - CUDA-specific code handles synchronization appropriately
 120 | - [ ] **MPS compatibility** - Metal Performance Shaders are considered if applicable
 121 | 
 122 | ### Memory Patterns
 123 | 
 124 | - [ ] **No memory leaks** - Temporary tensors are freed, no circular references
 125 | - [ ] **Efficient data structures** - Appropriate containers for access patterns
 126 | - [ ] **Gradient memory** - Proper use of `no_grad()`, `detach()` to avoid unnecessary graph retention
 127 | 
 128 | ### Common Performance Issues
 129 | 
 130 | - Creating new tensors inside training loops instead of pre-allocating
 131 | - Synchronous CUDA operations where async would work
 132 | - Keeping computation graph alive longer than needed
 133 | - Redundant clones or copies
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
  70 | 
  71 | **If blocked:** When a label is blocked by the hook, add ONLY `triage review` and stop. A human will handle it.
  72 | 
  73 | These rules are enforced by a PreToolUse hook that validates all labels against `labels.json`.
  74 | 
  75 | ---
  76 | 
  77 | ## Issue Triage (for each issue)
  78 | 
  79 | ### 0) Already Routed — SKIP
  80 | 
  81 | **If an issue already has ANY `oncall:` label, SKIP IT entirely.** Do not:
  82 | - Add any labels
  83 | - Add `triaged`
  84 | - Leave comments
  85 | - Do any triage work
  86 | 
  87 | That issue belongs to the sub-oncall team. They own their queue.
  88 | 
  89 | ### 1) Question vs Bug/Feature
  90 | 
  91 | - If it is a question (not a bug report or feature request): close and use the `redirect_to_forum` template from `templates.json`.
  92 | - If unclear whether it is a bug/feature vs a question: request additional information using the `request_more_info` template and stop.
  93 | 
  94 | ### 1.5) Needs Reproduction — External Files
  95 | 
  96 | Check if the issue body contains links to external files that users would need to download to reproduce.
  97 | 
  98 | **Patterns to detect:**
  99 | - File attachments: `.zip`, `.pt`, `.pth`, `.pkl`, `.safetensors`, `.onnx`, `.bin` files
 100 | - External storage: Google Drive, Dropbox, OneDrive, Mega, WeTransfer links
 101 | - Model hubs: Hugging Face Hub links to model files
 102 | 
 103 | **Action:**
 104 | 1. **Edit the issue body** to remove/redact the download links
 105 |    - Replace with: `[Link removed - external file downloads are not permitted for security reasons]`
 106 | 2. Add `needs reproduction` label
 107 | 3. Use the `needs_reproduction` template from `templates.json` to request a self-contained reproduction
 108 | 4. Do NOT add `triaged` — wait for the user to provide a reproducible example
 109 | 
 110 | ### 1.6) Edge Cases & Numerical Accuracy
 111 | 
 112 | If the issue involves extremal values or numerical precision differences:
 113 | 
 114 | **Patterns to detect:**
 115 | - Values near `torch.finfo(dtype).max` or `torch.finfo(dtype).min`
 116 | - NaN/Inf appearing in outputs from valid (but extreme) inputs
 117 | - Differences between CPU and GPU results
 118 | - Precision differences between dtypes (e.g., fp32 vs fp16)
 119 | - Fuzzer-generated edge cases
 120 | 
 121 | **Action:**
 122 | 1. Add `module: edge cases` label
 123 | 2. If from a fuzzer, also add `topic: fuzzer`
 124 | 3. Use the `numerical_accuracy` template from `templates.json` to link to the docs
 125 | 4. If the issue is clearly expected behavior per the docs, close it with the template comment
 126 | 
 127 | ### 2) Transfer (domain library or ExecuTorch)
 128 | 
 129 | If the issue belongs in another repo (vision/text/audio/RL/ExecuTorch/etc.), transfer the issue and **STOP**.
 130 | 
 131 | ### 2.5) PT2 Issues — Special Handling
 132 | 
 133 | When triaging PT2 issues (torch.compile, dynamo, inductor), see [pt2-triage-rubric.md](pt2-triage-rubric.md) for detailed labeling decisions.
 134 | 
 135 | **Key differences from general triage:**
 136 | - For PT2 issues, you MAY apply `module:` labels (e.g., `module: dynamo`, `module: inductor`, `module: dynamic shapes`)
 137 | - Use the rubric to determine the correct component labels
 138 | - Only redirect to `oncall: cpu inductor` for MKLDNN-specific issues; otherwise keep in PT2 queue
 139 | 
 140 | ### 3) Redirect to Secondary Oncall
 141 | 
 142 | **CRITICAL:** When redirecting issues to an oncall queue (**critical** with the exception of PT2), apply exactly one `oncall: ...` label and **STOP**. Do NOT:
 143 | - Add any `module:` labels
 144 | - Mark it `triaged`
 145 | - Do any further triage work
 146 | 
 147 | The sub-oncall team will handle their own triage. Your job is only to route it to them.
 148 | 
 149 | #### Oncall Redirect Labels
 150 | 
 151 | | Label | When to use |
 152 | |-------|-------------|
 153 | | `oncall: jit` | TorchScript issues |
 154 | | `oncall: distributed` | Distributed training (DDP, FSDP, RPC, c10d, DTensor, DeviceMesh, symmetric memory, context parallel, pipelining) |
 155 | | `oncall: export` | torch.export issues |
 156 | | `oncall: quantization` | Quantization issues |
 157 | | `oncall: mobile` | Mobile (iOS/Android), excludes ExecuTorch |
 158 | | `oncall: profiler` | Profiler issues (CPU, GPU, Kineto) |
 159 | | `oncall: visualization` | TensorBoard integration |
 160 | 
 161 | **Note:** `oncall: cpu inductor` is a sub-queue of PT2. For general triage, just use `oncall: pt2`.
 162 | 
 163 | ### 4) Label the issue (if NOT transferred/redirected)
 164 | 
 165 | Only if the issue stays in the general queue:
 166 | - Add 1+ `module: ...` labels based on the affected area
 167 | - If feature request: add `feature` (or `function request` for a new function or new arguments/modes)
 168 | - If small improvement: add `enhancement`
 169 | 
 170 | ### 5) High Priority — REQUIRES HUMAN REVIEW
 171 | 
 172 | **CRITICAL:** If you believe an issue is high priority, you MUST:
 173 | 1. Add `triage review` label and do not add `triaged`
 174 | 
 175 | Do NOT directly add `high priority` without human confirmation.
 176 | 
 177 | High priority criteria:
 178 | - Crash / segfault / illegal memory access
 179 | - Silent correctness issue (wrong results without error)
 180 | - Regression from a prior version
 181 | - Internal assert failure
 182 | - Many users affected
 183 | - Core component or popular model impact
 184 | 
 185 | ### 6) bot-triaged (automatic)
 186 | 
 187 | The `bot-triaged` label is automatically applied by a post-hook after any issue mutation. You do not need to add it manually.
 188 | 
 189 | ### 7) Mark triaged
 190 | 
 191 | If not transferred/redirected and not flagged for review, add `triaged`.
 192 | 
 193 | ---
 194 | 
 195 | ## V1 Constraints
 196 | 
 197 | **DO NOT:**
 198 | - Close bug reports or feature requests automatically
 199 | - Close issues unless they are clear usage questions per Step 1
 200 | - Assign issues to users
 201 | - Add `high priority` directly without human confirmation
 202 | - Add module labels when redirecting to oncall
 203 | - Add comments to bug reports or feature requests, except a single info request when classification is unclear
 204 | 
 205 | **DO:**
 206 | - Close clear usage questions and point to discuss.pytorch.org (per step 1)
 207 | - Be conservative - when in doubt, add `triage review` for human attention
 208 | - Apply type labels (`feature`, `enhancement`, `function request`) when confident
 209 | - Add `triaged` label when classification is complete
 210 | 
 211 | **Note:** `bot-triaged` is automatically applied by a post-hook after any issue mutation.
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
  24 |       "description": "Not as big of a feature, but technically not a bug. Should be easy to fix"
  25 |     },
  26 |     {
  27 |       "name": "feature",
  28 |       "description": "A request for a proper, new feature."
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
 144 |       "description": "Anything related to official binaries that we release to users"
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
 292 |       "description": ""
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
 388 |       "description": ""
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
 852 |       "description": "All things related to torch.nn.functional.scaled_dot_product_attentiion"
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
  34 | ## 3. Don't Over-Tag pt2-dispatcher
  35 | 
  36 | `module: pt2-dispatcher` is for bugs **IN** the dispatcher code, not just when it appears in a stack trace.
  37 | 
  38 | **Common mistake:** Seeing `_aot_autograd/` in a stack trace and assuming it's a pt2-dispatcher bug. The dispatcher code is on the call path for almost everything - that doesn't mean the bug is there.
  39 | 
  40 | **Only add pt2-dispatcher when:**
  41 | - The bug is clearly in AOT autograd logic (e.g., incorrect tensor metadata handling)
  42 | - The bug is in functionalization
  43 | - The bug is in FakeTensor implementation
  44 | - The bug is in custom operator registration/dispatch
  45 | 
  46 | **Don't add pt2-dispatcher when:**
  47 | - AOT autograd just happens to be on the stack trace
  48 | - The actual bug is in functorch transforms (use `module: functorch` instead)
  49 | - The actual bug is in inductor codegen (use `module: inductor` instead)
  50 | - You're not sure where the bug actually is
  51 | 
  52 | ---
  53 | 
  54 | ## 4. Don't Redirect When PT2 Owns the Code
  55 | 
  56 | **This is critical:** Don't redirect to another oncall just because their subsystem is *involved*. Only redirect when:
  57 | 1. The bug is clearly **IN** their code, AND
  58 | 2. PT2 code is not at fault
  59 | 
  60 | **Examples - DO NOT redirect:**
  61 | 
  62 | | Situation | Why NOT redirect |
  63 | |-----------|------------------|
  64 | | Export triggers a bug, but the bug is a leaked hook in AOT autograd | Bug is in PT2 code → PT2 owns it |
  65 | | DTensor has a bad error message under compile | Bug is in PT2's error handling → PT2 owns UX |
  66 | | Distributed training fails, but stack trace shows inductor issue | Bug is in inductor → PT2 owns it |
  67 | 
  68 | **Examples - DO redirect:**
  69 | 
  70 | | Situation | Why redirect |
  71 | |-----------|--------------|
  72 | | MKLDNN-specific codegen bug | `oncall: cpu inductor` owns MKLDNN |
  73 | | Export-only issue with no compile involvement | `oncall: export` owns it |
  74 | | Bug in DTensor's tensor subclass implementation | `oncall: distributed` owns DTensor internals |
  75 | 
  76 | **The test:** Ask "where would the fix need to be made?" If the fix is in PT2 code, PT2 owns it.
  77 | 
  78 | **Adding labels for visibility:** You CAN add domain labels (e.g., `module: dtensor`) so domain experts see the issue, but don't ADD the oncall redirect label unless you're actually handing it off.
  79 | 
  80 | ---
  81 | 
  82 | ## 5. Add Domain-Specific Labels for Visibility
  83 | 
  84 | Even when not redirecting, add labels so domain experts see the issue:
  85 | 
  86 | | Domain | Label |
  87 | |--------|-------|
  88 | | DTensor | `module: dtensor` |
  89 | | FSDP | `module: fsdp` |
  90 | | DDP | `module: ddp` |
  91 | | Flex attention | `module: flex attention` |
  92 | 
  93 | ---
  94 | 
  95 | ## 6. Use Feature-Specific Labels
  96 | 
  97 | Check for existing labels before inventing categories:
  98 | 
  99 | | Feature | Label |
 100 | |---------|-------|
 101 | | Caching issues | `compile-cache` |
 102 | | Determinism | `module: determinism` |
 103 | | Compile/startup time | `module: compile-time` |
 104 | | Numerical issues | `module: numerical-stability` |
 105 | | UX/error messages | `module: compile ux` |
 106 | 
 107 | ---
 108 | 
 109 | ## 7. functorch + compile
 110 | 
 111 | | Situation | Labels |
 112 | |-----------|--------|
 113 | | Compiling a functorch transform (vjp, grad, vmap) | `module: functorch`, `dynamo-functorch` |
 114 | | Only add `pt2-dispatcher` if stack trace shows AOT autograd | Check stack trace first |
 115 | 
 116 | ---
 117 | 
 118 | ## 8. High Priority Criteria
 119 | 
 120 | Mark `high priority` if ANY of these apply:
 121 | 
 122 | | Criteria | Example |
 123 | |----------|---------|
 124 | | **Crash** (segfault, illegal memory access) | Device-side assert, SIGSEGV |
 125 | | **Silently wrong results** | Output differs from eager with no error |
 126 | | **Regression** | "This used to work in version X" |
 127 | | **Flaky test** | Usually indicates regression |
 128 | | **Important model regressed** (>10% perf) | Common model, significant slowdown |
 129 | | **Important customer** | Huggingface, common usage patterns |
 130 | 
 131 | Note: Adding `high priority` auto-adds `triage review` for discussion.
 132 | 
 133 | ---
 134 | 
 135 | ## 9. Fuzzer Issues
 136 | 
 137 | For `topic: fuzzer` issues:
 138 | 
 139 | 1. Ensure rtol/atol are at default tolerances
 140 | 2. Don't compare indices of max/min (avoids tolerance issues)
 141 | 3. Use `torch._dynamo.utils.same` with `fp64_ref` for comparison
 142 | 4. If criteria met and bug appears easy/common → triage normally
 143 | 5. If complex and rare → add `low priority`
 144 | 
 145 | ---
 146 | 
 147 | ## 10. Quick Label Reference
 148 | 
 149 | ### Core Components
 150 | - `module: dynamo` - Tracing, bytecode, graph breaks
 151 | - `module: inductor` - Codegen, Triton kernels
 152 | - `module: dynamic shapes` - Symbolic shapes, guards, data-dependent
 153 | - `module: pt2-dispatcher` - AOT autograd, functionalization, FakeTensor
 154 | - `module: cuda graphs` - CUDA graph capture/replay
 155 | - `module: flex attention` - Flex attention API
 156 | 
 157 | ### Holistic Areas
 158 | - `module: compile ux` - Error messages, APIs, programming model
 159 | - `module: startup-compile-tracing time` - Compilation speed
 160 | - `module: performance` - Runtime performance
 161 | - `module: memory usage` - Memory issues
 162 | 
 163 | ### Status Labels
 164 | - `triaged` - Done triaging
 165 | - `triage review` - Discuss at meeting
 166 | - `needs reproduction` - Blocked on repro
 167 | - `needs research` - Needs investigation
 168 | - `actionable` - Clear what to do
 169 | 
 170 | ### Redirects
 171 | - `oncall: cpu inductor` - CPU/MKLDNN issues
 172 | - `oncall: export` - Export-specific issues
 173 | - `oncall: distributed` - Distributed training issues
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
  42 | ]
  43 | 
  44 | REDUNDANT_PAIRS = [
  45 |     ("module: rnn", "module: nn"),
  46 | ]
  47 | 
  48 | 
  49 | def debug_log(msg: str, to_stderr: bool = False):
  50 |     timestamp = datetime.now().isoformat()
  51 |     formatted = f"[{timestamp}] [PreToolUse] {msg}"
  52 |     try:
  53 |         with open(DEBUG_LOG, "a") as f:
  54 |             f.write(formatted + "\n")
  55 |     except Exception:
  56 |         pass
  57 |     if to_stderr or os.environ.get("TRIAGE_HOOK_VERBOSE"):
  58 |         print(f"[DEBUG] {formatted}", file=sys.stderr)
  59 | 
  60 | 
  61 | def is_forbidden(label: str) -> bool:
  62 |     label_lower = label.lower()
  63 |     for pattern in FORBIDDEN_PATTERNS:
  64 |         if re.search(pattern, label_lower):
  65 |             return True
  66 |     return label_lower in [f.lower() for f in FORBIDDEN_EXACT]
  67 | 
  68 | 
  69 | def load_valid_labels() -> set[str]:
  70 |     try:
  71 |         with open(LABELS_FILE) as f:
  72 |             data = json.load(f)
  73 |     except FileNotFoundError:
  74 |         raise RuntimeError(f"labels.json not found at {LABELS_FILE}") from None
  75 |     except json.JSONDecodeError as e:
  76 |         raise RuntimeError(f"labels.json contains invalid JSON: {e}") from None
  77 |     except PermissionError:
  78 |         raise RuntimeError("Cannot read labels.json: permission denied") from None
  79 | 
  80 |     labels_list = data.get("labels", [])
  81 |     try:
  82 |         return {label["name"] for label in labels_list}
  83 |     except (KeyError, TypeError) as e:
  84 |         raise RuntimeError(f"labels.json has malformed entries: {e}") from None
  85 | 
  86 | 
  87 | def strip_redundant(labels: list[str]) -> tuple[list[str], list[str]]:
  88 |     labels_set = set(labels)
  89 |     to_remove = set()
  90 |     for specific, general in REDUNDANT_PAIRS:
  91 |         if specific in labels_set and general in labels_set:
  92 |             to_remove.add(general)
  93 |     return [l for l in labels if l not in to_remove], sorted(to_remove)
  94 | 
  95 | 
  96 | def fetch_existing_labels(owner: str, repo: str, issue_number: int) -> list[str]:
  97 |     result = subprocess.run(
  98 |         [
  99 |             "gh",
 100 |             "issue",
 101 |             "view",
 102 |             str(issue_number),
 103 |             "--repo",
 104 |             f"{owner}/{repo}",
 105 |             "--json",
 106 |             "labels",
 107 |         ],
 108 |         capture_output=True,
 109 |         text=True,
 110 |         check=False,
 111 |         timeout=15,
 112 |     )
 113 |     if result.returncode != 0:
 114 |         raise RuntimeError(
 115 |             f"Cannot fetch existing labels (gh exit {result.returncode}): "
 116 |             f"{result.stderr.strip()}"
 117 |         )
 118 |     data = json.loads(result.stdout)
 119 |     return [label["name"] for label in data.get("labels", [])]
 120 | 
 121 | 
 122 | def allow_with_updated_input(tool_input: dict, merged_labels: list[str]) -> None:
 123 |     updated = dict(tool_input)
 124 |     updated["labels"] = merged_labels
 125 |     json.dump(
 126 |         {
 127 |             "hookSpecificOutput": {
 128 |                 "hookEventName": "PreToolUse",
 129 |                 "permissionDecision": "allow",
 130 |                 "updatedInput": updated,
 131 |             }
 132 |         },
 133 |         sys.stdout,
 134 |     )
 135 |     sys.exit(0)
 136 | 
 137 | 
 138 | def main():
 139 |     try:
 140 |         data = json.load(sys.stdin)
 141 |         debug_log(f"Hook invoked with data: {json.dumps(data, indent=2)}")
 142 |         tool_input = data.get("tool_input", {})
 143 | 
 144 |         requested_labels = tool_input.get("labels", []) or []
 145 |         debug_log(f"Labels requested: {requested_labels}")
 146 | 
 147 |         if not requested_labels:
 148 |             debug_log("No labels provided, allowing")
 149 |             sys.exit(0)
 150 | 
 151 |         owner = tool_input.get("owner", "pytorch")
 152 |         repo = tool_input.get("repo", "pytorch")
 153 |         issue_number = tool_input.get("issue_number")
 154 |         if not issue_number:
 155 |             raise RuntimeError("tool_input missing issue_number")
 156 | 
 157 |         forbidden = [l for l in requested_labels if is_forbidden(l)]
 158 |         clean_labels = [l for l in requested_labels if not is_forbidden(l)]
 159 | 
 160 |         if forbidden:
 161 |             debug_log(f"Stripped forbidden labels: {forbidden}")
 162 |             if not clean_labels:
 163 |                 clean_labels = ["triage review"]
 164 |             elif "triage review" not in clean_labels:
 165 |                 clean_labels.append("triage review")
 166 |             print(
 167 |                 f"Stripped forbidden labels (require human decision): {forbidden}. "
 168 |                 f"Added 'triage review' for human attention.",
 169 |                 file=sys.stderr,
 170 |             )
 171 | 
 172 |         valid_labels = load_valid_labels()
 173 |         nonexistent = [l for l in clean_labels if l not in valid_labels]
 174 |         clean_labels = [l for l in clean_labels if l in valid_labels]
 175 | 
 176 |         if nonexistent:
 177 |             debug_log(f"Stripped non-existent labels: {nonexistent}")
 178 |             print(
 179 |                 f"Stripped non-existent labels: {nonexistent}",
 180 |                 file=sys.stderr,
 181 |             )
 182 | 
 183 |         clean_labels, removed_redundant = strip_redundant(clean_labels)
 184 |         if removed_redundant:
 185 |             debug_log(f"Stripped redundant labels: {removed_redundant}")
 186 |             print(
 187 |                 f"Stripped redundant labels: {removed_redundant}",
 188 |                 file=sys.stderr,
 189 |             )
 190 | 
 191 |         if not clean_labels:
 192 |             debug_log("No valid labels remain after filtering, blocking")
 193 |             print(
 194 |                 "All requested labels were invalid. No labels to apply.",
 195 |                 file=sys.stderr,
 196 |             )
 197 |             sys.exit(2)
 198 | 
 199 |         existing_labels = fetch_existing_labels(owner, repo, issue_number)
 200 |         debug_log(f"Existing labels on issue: {existing_labels}")
 201 | 
 202 |         merged = sorted(set(existing_labels) | set(clean_labels))
 203 |         debug_log(f"Merged labels (existing + new): {merged}")
 204 | 
 205 |         allow_with_updated_input(tool_input, merged)
 206 | 
 207 |     except json.JSONDecodeError as e:
 208 |         debug_log(f"JSON decode error: {e}")
 209 |         print(f"Hook error: Invalid JSON input: {e}", file=sys.stderr)
 210 |         print("Hook was unable to validate labels; stopping triage.", file=sys.stderr)
 211 |         sys.exit(2)
 212 |     except Exception as e:
 213 |         debug_log(f"Unexpected error: {type(e).__name__}: {e}")
 214 |         print(f"Hook error: {e}", file=sys.stderr)
 215 |         print("Hook was unable to validate labels; stopping triage.", file=sys.stderr)
 216 |         sys.exit(2)
 217 | 
 218 | 
 219 | if __name__ == "__main__":
 220 |     main()
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
   1 | # Environment
   2 | 
   3 | If any tool you're trying to use (pip, python, spin, etc) is missing, always stop and ask the user if an environment is needed. Do NOT try to find alternatives or install these tools.
   4 | 
   5 | # Build
   6 | 
   7 | Always ask for build configuration environment variables before running build.
   8 | All build (both codegen, C++ and python) is done via `pip install -e . -v --no-build-isolation`.
   9 | You should NEVER run any other command to build PyTorch.
  10 | 
  11 | # Testing
  12 | 
  13 | Use our test class and test runner:
  14 | 
  15 | ```
  16 | from torch.testing._internal.common_utils import run_tests, TestCase
  17 | 
  18 | class TestFeature(TestCase):
  19 |     ...
  20 | 
  21 | if __name__ == "__main__":
  22 |     run_tests()
  23 | ```
  24 | 
  25 | To test Tensor equality, use assertEqual.
  26 | 
  27 | # Linting
  28 | 
  29 | Only use commands provided via `spin` for linting.
  30 | Use `spin help` to list available commands.
  31 | Generally, use `spin lint` as to run the lint and `spin fixlint` to apply automatic fixes.
  32 | 
  33 | # Commit messages
  34 | 
  35 | Don't commit unless the user explicitly asks you to.
  36 | 
  37 | When writing a commit message, don't make a bullet list of the individual
  38 | changes. Instead, if the PR is large, explain the order to review changes
  39 | (e.g., the logical progression), or if it's short just omit the bullet list
  40 | entirely.
  41 | 
  42 | Disclose that the PR was authored with Claude.
  43 | 
  44 | # Coding Style Guidelines
  45 | 
  46 | Follow these rules for all code changes in this repository:
  47 | 
  48 | - Minimize comments; be concise; code should be self-explanatory and self-documenting.
  49 | - Comments should be useful, for example, comments that remind the reader about
  50 |   some global context that is non-obvious and can't be inferred locally.
  51 | - Don't make trivial (1-2 LOC) helper functions that are only used once unless
  52 |   it significantly improves code readability.
  53 | - Prefer clear abstractions. State management should be explicit.
  54 |   For example, if managing state in a Python class: there should be a clear
  55 |   class definition that has all of the members: don't dynamically `setattr`
  56 |   a field on an object and then dynamically `getattr` the field on the object.
  57 | - Match existing code style and architectural patterns.
  58 | - Assume the reader has familiarity with PyTorch. They may not be the expert
  59 |   on the code that is being read, but they should have some experience in the
  60 |   area.
  61 | 
  62 | If uncertain, choose the simpler, more concise implementation.
  63 | 
  64 | # Dynamo Config
  65 | 
  66 | Use `torch._dynamo.config.patch` for temporarily changing config. It can be used as a decorator on test methods or as a context manager:
  67 | 
  68 | ```python
  69 | # Good - use patch as decorator on test method
  70 | @torch._dynamo.config.patch(force_compile_during_fx_trace=True)
  71 | def test_my_feature(self):
  72 |     # test code here
  73 |     pass
  74 | 
  75 | # Good - use patch as context manager
  76 | with torch._dynamo.config.patch(force_compile_during_fx_trace=True):
  77 |     # test code here
  78 |     pass
  79 | 
  80 | # Bad - manual save/restore
  81 | orig = torch._dynamo.config.force_compile_during_fx_trace
  82 | try:
  83 |     torch._dynamo.config.force_compile_during_fx_trace = True
  84 |     # test code here
  85 | finally:
  86 |     torch._dynamo.config.force_compile_during_fx_trace = orig
  87 | ```
  88 | 
  89 | # Fixing B950 line too long in multi-line string blocks
  90 | 
  91 | If B950 line too long triggers on a multi-line string block, you cannot fix it by
  92 | putting # noqa: B950 on that line directly, as that would change the meaning of the
  93 | string, nor can you fix it by line breaking the string (since you need the string
  94 | to stay the same).  Instead, put # noqa: B950 on the same line as the terminating
  95 | triple quote.
  96 | 
  97 | Example:
  98 | 
  99 | ```
 100 |     self.assertExpectedInline(
 101 |         foo(),
 102 |         """
 103 | this line is too long...
 104 | """,  # noqa: B950
 105 |     )
 106 | ```
 107 | 
 108 | # Logging and Structured Tracing
 109 | 
 110 | When adding debug logging for errors or diagnostic info, consider two user personas:
 111 | 
 112 | 1. **Local development**: Users run locally and can access files on disk
 113 | 2. **Production jobs**: Users can only access logs via `tlparse` from structured traces
 114 | 
 115 | For production debugging, use `trace_structured` to log artifacts:
 116 | 
 117 | ```python
 118 | from torch._logging import trace_structured
 119 | 
 120 | # Log an artifact (graph, edge list, etc.)
 121 | trace_structured(
 122 |     "artifact",
 123 |     metadata_fn=lambda: {
 124 |         "name": "my_debug_artifact",
 125 |         "encoding": "string",
 126 |     },
 127 |     payload_fn=lambda: my_content_string,
 128 | )
 129 | ```
 130 | 
 131 | To check if structured tracing is enabled (for conditional messaging):
 132 | 
 133 | ```python
 134 | from torch._logging._internal import trace_log
 135 | 
 136 | if trace_log.handlers:
 137 |     # Structured tracing is enabled, suggest tlparse in error messages
 138 |     msg += "[Use tlparse to extract debug artifacts]"
 139 | ```
 140 | 
 141 | **Best practices for error diagnostics:**
 142 | 
 143 | - Always log to `trace_structured` for production (no runtime cost if disabled)
 144 | - If you're dumping debug info in the event of a true internal compiler exception,
 145 |   you can also consider writing to local files for local debugging convenience
 146 | - In error messages, tell users about both options:
 147 |   - Local files: "FX graph dump: min_cut_failed_graph.txt"
 148 |   - Production: "Use tlparse to extract artifacts" (only if tracing enabled)
 149 | - Use `_get_unique_path()` pattern to avoid overwriting existing debug files
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
  38 |     - [Building a PDF](#building-a-pdf)
  39 |   - [Previous Versions](#previous-versions)
  40 | - [Getting Started](#getting-started)
  41 | - [Resources](#resources)
  42 | - [Communication](#communication)
  43 | - [Releases and Contributing](#releases-and-contributing)
  44 | - [The Team](#the-team)
  45 | - [License](#license)
  46 | 
  47 | <!-- tocstop -->
  48 | 
  49 | ## More About PyTorch
  50 | 
  51 | [Learn the basics of PyTorch](https://pytorch.org/tutorials/beginner/basics/intro.html)
  52 | 
  53 | At a granular level, PyTorch is a library that consists of the following components:
  54 | 
  55 | | Component | Description |
  56 | | ---- | --- |
  57 | | [**torch**](https://pytorch.org/docs/stable/torch.html) | A Tensor library like NumPy, with strong GPU support |
  58 | | [**torch.autograd**](https://pytorch.org/docs/stable/autograd.html) | A tape-based automatic differentiation library that supports all differentiable Tensor operations in torch |
  59 | | [**torch.jit**](https://pytorch.org/docs/stable/jit.html) | A compilation stack (TorchScript) to create serializable and optimizable models from PyTorch code  |
  60 | | [**torch.nn**](https://pytorch.org/docs/stable/nn.html) | A neural networks library deeply integrated with autograd designed for maximum flexibility |
  61 | | [**torch.multiprocessing**](https://pytorch.org/docs/stable/multiprocessing.html) | Python multiprocessing, but with magical memory sharing of torch Tensors across processes. Useful for data loading and Hogwild training |
  62 | | [**torch.utils**](https://pytorch.org/docs/stable/data.html) | DataLoader and other utility functions for convenience |
  63 | 
  64 | Usually, PyTorch is used either as:
  65 | 
  66 | - A replacement for NumPy to use the power of GPUs.
  67 | - A deep learning research platform that provides maximum flexibility and speed.
  68 | 
  69 | Elaborating Further:
  70 | 
  71 | ### A GPU-Ready Tensor Library
  72 | 
  73 | If you use NumPy, then you have used Tensors (a.k.a. ndarray).
  74 | 
  75 | ![Tensor illustration](https://github.com/pytorch/pytorch/raw/main/docs/source/_static/img/tensor_illustration.png)
  76 | 
  77 | PyTorch provides Tensors that can live either on the CPU or the GPU and accelerates the
  78 | computation by a huge amount.
  79 | 
  80 | We provide a wide variety of tensor routines to accelerate and fit your scientific computation needs
  81 | such as slicing, indexing, mathematical operations, linear algebra, reductions.
  82 | And they are fast!
  83 | 
  84 | ### Dynamic Neural Networks: Tape-Based Autograd
  85 | 
  86 | PyTorch has a unique way of building neural networks: using and replaying a tape recorder.
  87 | 
  88 | Most frameworks such as TensorFlow, Theano, Caffe, and CNTK have a static view of the world.
  89 | One has to build a neural network and reuse the same structure again and again.
  90 | Changing the way the network behaves means that one has to start from scratch.
  91 | 
  92 | With PyTorch, we use a technique called reverse-mode auto-differentiation, which allows you to
  93 | change the way your network behaves arbitrarily with zero lag or overhead. Our inspiration comes
  94 | from several research papers on this topic, as well as current and past work such as
  95 | [torch-autograd](https://github.com/twitter/torch-autograd),
  96 | [autograd](https://github.com/HIPS/autograd),
  97 | [Chainer](https://chainer.org), etc.
  98 | 
  99 | While this technique is not unique to PyTorch, it's one of the fastest implementations of it to date.
 100 | You get the best of speed and flexibility for your crazy research.
 101 | 
 102 | ![Dynamic graph](https://github.com/pytorch/pytorch/raw/main/docs/source/_static/img/dynamic_graph.gif)
 103 | 
 104 | ### Python First
 105 | 
 106 | PyTorch is not a Python binding into a monolithic C++ framework.
 107 | It is built to be deeply integrated into Python.
 108 | You can use it naturally like you would use [NumPy](https://www.numpy.org/) / [SciPy](https://www.scipy.org/) / [scikit-learn](https://scikit-learn.org) etc.
 109 | You can write your new neural network layers in Python itself, using your favorite libraries
 110 | and use packages such as [Cython](https://cython.org/) and [Numba](http://numba.pydata.org/).
 111 | Our goal is to not reinvent the wheel where appropriate.
 112 | 
 113 | ### Imperative Experiences
 114 | 
 115 | PyTorch is designed to be intuitive, linear in thought, and easy to use.
 116 | When you execute a line of code, it gets executed. There isn't an asynchronous view of the world.
 117 | When you drop into a debugger or receive error messages and stack traces, understanding them is straightforward.
 118 | The stack trace points to exactly where your code was defined.
 119 | We hope you never spend hours debugging your code because of bad stack traces or asynchronous and opaque execution engines.
 120 | 
 121 | ### Fast and Lean
 122 | 
 123 | PyTorch has minimal framework overhead. We integrate acceleration libraries
 124 | such as [Intel MKL](https://software.intel.com/mkl) and NVIDIA ([cuDNN](https://developer.nvidia.com/cudnn), [NCCL](https://developer.nvidia.com/nccl)) to maximize speed.
 125 | At the core, its CPU and GPU Tensor and neural network backends
 126 | are mature and have been tested for years.
 127 | 
 128 | Hence, PyTorch is quite fast — whether you run small or large neural networks.
 129 | 
 130 | The memory usage in PyTorch is extremely efficient compared to Torch or some of the alternatives.
 131 | We've written custom memory allocators for the GPU to make sure that
 132 | your deep learning models are maximally memory efficient.
 133 | This enables you to train bigger deep learning models than before.
 134 | 
 135 | ### Extensions Without Pain
 136 | 
 137 | Writing new neural network modules, or interfacing with PyTorch's Tensor API was designed to be straightforward
 138 | and with minimal abstractions.
 139 | 
 140 | You can write new neural network layers in Python using the torch API
 141 | [or your favorite NumPy-based libraries such as SciPy](https://pytorch.org/tutorials/advanced/numpy_extensions_tutorial.html).
 142 | 
 143 | If you want to write your layers in C/C++, we provide a convenient extension API that is efficient and with minimal boilerplate.
 144 | No wrapper code needs to be written. You can see [a tutorial here](https://pytorch.org/tutorials/advanced/cpp_extension.html) and [an example here](https://github.com/pytorch/extension-cpp).
 145 | 
 146 | 
 147 | ## Installation
 148 | 
 149 | ### Binaries
 150 | Commands to install binaries via Conda or pip wheels are on our website: [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)
 151 | 
 152 | 
 153 | #### NVIDIA Jetson Platforms
 154 | 
 155 | Python wheels for NVIDIA's Jetson Nano, Jetson TX1/TX2, Jetson Xavier NX/AGX, and Jetson AGX Orin are provided [here](https://forums.developer.nvidia.com/t/pytorch-for-jetson-version-1-10-now-available/72048) and the L4T container is published [here](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-pytorch)
 156 | 
 157 | They require JetPack 4.2 and above, and [@dusty-nv](https://github.com/dusty-nv) and [@ptrblck](https://github.com/ptrblck) are maintaining them.
 158 | 
 159 | 
 160 | ### From Source
 161 | 
 162 | #### Prerequisites
 163 | If you are installing from source, you will need:
 164 | - Python 3.10 or later
 165 | - A compiler that fully supports C++17, such as clang or gcc (gcc 9.4.0 or newer is required, on Linux)
 166 | - Visual Studio or Visual Studio Build Tool (Windows only)
 167 | 
 168 | \* PyTorch CI uses Visual C++ BuildTools, which come with Visual Studio Enterprise,
 169 | Professional, or Community Editions. You can also install the build tools from
 170 | https://visualstudio.microsoft.com/visual-cpp-build-tools/. The build tools *do not*
 171 | come with Visual Studio Code by default.
 172 | 
 173 | An example of environment setup is shown below:
 174 | 
 175 | * Linux:
 176 | 
 177 | ```bash
 178 | $ source <CONDA_INSTALL_DIR>/bin/activate
 179 | $ conda create -y -n <CONDA_NAME>
 180 | $ conda activate <CONDA_NAME>
 181 | ```
 182 | 
 183 | * Windows:
 184 | 
 185 | ```bash
 186 | $ source <CONDA_INSTALL_DIR>\Scripts\activate.bat
 187 | $ conda create -y -n <CONDA_NAME>
 188 | $ conda activate <CONDA_NAME>
 189 | $ call "C:\Program Files\Microsoft Visual Studio\<VERSION>\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
 190 | ```
 191 | 
 192 | A conda environment is not required.  You can also do a PyTorch build in a
 193 | standard virtual environment, e.g., created with tools like `uv`, provided
 194 | your system has installed all the necessary dependencies unavailable as pip
 195 | packages (e.g., CUDA, MKL.)
 196 | 
 197 | ##### NVIDIA CUDA Support
 198 | If you want to compile with CUDA support, [select a supported version of CUDA from our support matrix](https://pytorch.org/get-started/locally/), then install the following:
 199 | - [NVIDIA CUDA](https://developer.nvidia.com/cuda-downloads)
 200 | - [NVIDIA cuDNN](https://developer.nvidia.com/cudnn) v8.5 or above
 201 | - [Compiler](https://gist.github.com/ax3l/9489132) compatible with CUDA
 202 | 
 203 | Note: You could refer to the [cuDNN Support Matrix](https://docs.nvidia.com/deeplearning/cudnn/backend/latest/reference/support-matrix.html) for cuDNN versions with the various supported CUDA, CUDA driver, and NVIDIA hardware.
 204 | 
 205 | If you want to disable CUDA support, export the environment variable `USE_CUDA=0`.
 206 | Other potentially useful environment variables may be found in `setup.py`.  If
 207 | CUDA is installed in a non-standard location, set PATH so that the nvcc you
 208 | want to use can be found (e.g., `export PATH=/usr/local/cuda-12.8/bin:$PATH`).
 209 | 
 210 | If you are building for NVIDIA's Jetson platforms (Jetson Nano, TX1, TX2, AGX Xavier), Instructions to install PyTorch for Jetson Nano are [available here](https://devtalk.nvidia.com/default/topic/1049071/jetson-nano/pytorch-for-jetson-nano/)
 211 | 
 212 | ##### AMD ROCm Support
 213 | If you want to compile with ROCm support, install
 214 | - [AMD ROCm](https://rocm.docs.amd.com/en/latest/deploy/linux/quick_start.html) 4.0 and above installation
 215 | - ROCm is currently supported only for Linux systems.
 216 | 
 217 | By default the build system expects ROCm to be installed in `/opt/rocm`. If ROCm is installed in a different directory, the `ROCM_PATH` environment variable must be set to the ROCm installation directory. The build system automatically detects the AMD GPU architecture. Optionally, the AMD GPU architecture can be explicitly set with the `PYTORCH_ROCM_ARCH` environment variable [AMD GPU architecture](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html#supported-gpus)
 218 | 
 219 | If you want to disable ROCm support, export the environment variable `USE_ROCM=0`.
 220 | Other potentially useful environment variables may be found in `setup.py`.
 221 | 
 222 | ##### Intel GPU Support
 223 | If you want to compile with Intel GPU support, follow these
 224 | - [PyTorch Prerequisites for Intel GPUs](https://www.intel.com/content/www/us/en/developer/articles/tool/pytorch-prerequisites-for-intel-gpu.html) instructions.
 225 | - Intel GPU is supported for Linux and Windows.
 226 | 
 227 | If you want to disable Intel GPU support, export the environment variable `USE_XPU=0`.
 228 | Other potentially useful environment variables may be found in `setup.py`.
 229 | 
 230 | #### Get the PyTorch Source
 231 | 
 232 | ```bash
 233 | git clone https://github.com/pytorch/pytorch
 234 | cd pytorch
 235 | # if you are updating an existing checkout
 236 | git submodule sync
 237 | git submodule update --init --recursive
 238 | ```
 239 | 
 240 | #### Install Dependencies
 241 | 
 242 | **Common**
 243 | 
 244 | ```bash
 245 | # Run this command from the PyTorch directory after cloning the source code using the “Get the PyTorch Source“ section above
 246 | pip install --group dev
 247 | ```
 248 | 
 249 | **On Linux**
 250 | 
 251 | ```bash
 252 | pip install mkl-static mkl-include
 253 | # CUDA only: Add LAPACK support for the GPU if needed
 254 | # magma installation: run with active conda environment. specify CUDA version to install
 255 | .ci/docker/common/install_magma_conda.sh 12.4
 256 | 
 257 | # (optional) If using torch.compile with inductor/triton, install the matching version of triton
 258 | # Run from the pytorch directory after cloning
 259 | # For Intel GPU support, please explicitly `export USE_XPU=1` before running command.
 260 | make triton
 261 | ```
 262 | 
 263 | **On MacOS**
 264 | 
 265 | ```bash
 266 | # Add this package on intel x86 processor machines only
 267 | pip install mkl-static mkl-include
 268 | # Add these packages if torch.distributed is needed
 269 | conda install pkg-config libuv
 270 | ```
 271 | 
 272 | **On Windows**
 273 | 
 274 | ```bash
 275 | pip install mkl-static mkl-include
 276 | # Add these packages if torch.distributed is needed.
 277 | # Distributed package support on Windows is a prototype feature and is subject to changes.
 278 | conda install -c conda-forge libuv=1.51
 279 | ```
 280 | 
 281 | #### Install PyTorch
 282 | 
 283 | **On Linux**
 284 | 
 285 | If you're compiling for AMD ROCm then first run this command:
 286 | 
 287 | ```bash
 288 | # Only run this if you're compiling for ROCm
 289 | python tools/amd_build/build_amd.py
 290 | ```
 291 | 
 292 | Install PyTorch
 293 | 
 294 | ```bash
 295 | # the CMake prefix for conda environment
 296 | export CMAKE_PREFIX_PATH="${CONDA_PREFIX:-'$(dirname $(which conda))/../'}:${CMAKE_PREFIX_PATH}"
 297 | python -m pip install --no-build-isolation -v -e .
 298 | 
 299 | # the CMake prefix for non-conda environment, e.g. Python venv
 300 | # call following after activating the venv
 301 | export CMAKE_PREFIX_PATH="${VIRTUAL_ENV}:${CMAKE_PREFIX_PATH}"
 302 | ```
 303 | 
 304 | **On macOS**
 305 | 
 306 | ```bash
 307 | python -m pip install --no-build-isolation -v -e .
 308 | ```
 309 | 
 310 | **On Windows**
 311 | 
 312 | If you want to build legacy python code, please refer to [Building on legacy code and CUDA](https://github.com/pytorch/pytorch/blob/main/CONTRIBUTING.md#building-on-legacy-code-and-cuda)
 313 | 
 314 | **CPU-only builds**
 315 | 
 316 | In this mode PyTorch computations will run on your CPU, not your GPU.
 317 | 
 318 | ```cmd
 319 | python -m pip install --no-build-isolation -v -e .
 320 | ```
 321 | 
 322 | Note on OpenMP: The desired OpenMP implementation is Intel OpenMP (iomp). In order to link against iomp, you'll need to manually download the library and set up the building environment by tweaking `CMAKE_INCLUDE_PATH` and `LIB`. The instruction [here](https://github.com/pytorch/pytorch/blob/main/docs/source/notes/windows.rst#building-from-source) is an example for setting up both MKL and Intel OpenMP. Without these configurations for CMake, Microsoft Visual C OpenMP runtime (vcomp) will be used.
 323 | 
 324 | **CUDA based build**
 325 | 
 326 | In this mode PyTorch computations will leverage your GPU via CUDA for faster number crunching
 327 | 
 328 | [NVTX](https://docs.nvidia.com/gameworks/content/gameworkslibrary/nvtx/nvidia_tools_extension_library_nvtx.htm) is needed to build PyTorch with CUDA.
 329 | NVTX is a part of CUDA distributive, where it is called "Nsight Compute". To install it onto an already installed CUDA run CUDA installation once again and check the corresponding checkbox.
 330 | Make sure that CUDA with Nsight Compute is installed after Visual Studio.
 331 | 
 332 | Currently, VS 2017 / 2019, and Ninja are supported as the generator of CMake. If `ninja.exe` is detected in `PATH`, then Ninja will be used as the default generator, otherwise, it will use VS 2017 / 2019.
 333 | <br/> If Ninja is selected as the generator, the latest MSVC will get selected as the underlying toolchain.
 334 | 
 335 | Additional libraries such as
 336 | [Magma](https://developer.nvidia.com/magma), [oneDNN, a.k.a. MKLDNN or DNNL](https://github.com/oneapi-src/oneDNN), and [Sccache](https://github.com/mozilla/sccache) are often needed. Please refer to the [installation-helper](https://github.com/pytorch/pytorch/tree/main/.ci/pytorch/win-test-helpers/installation-helpers) to install them.
 337 | 
 338 | You can refer to the [build_pytorch.bat](https://github.com/pytorch/pytorch/blob/main/.ci/pytorch/win-test-helpers/build_pytorch.bat) script for some other environment variables configurations
 339 | 
 340 | ```cmd
 341 | cmd
 342 | 
 343 | :: Set the environment variables after you have downloaded and unzipped the mkl package,
 344 | :: else CMake would throw an error as `Could NOT find OpenMP`.
 345 | set CMAKE_INCLUDE_PATH={Your directory}\mkl\include
 346 | set LIB={Your directory}\mkl\lib;%LIB%
 347 | 
 348 | :: Read the content in the previous section carefully before you proceed.
 349 | :: [Optional] If you want to override the underlying toolset used by Ninja and Visual Studio with CUDA, please run the following script block.
 350 | :: "Visual Studio 2019 Developer Command Prompt" will be run automatically.
 351 | :: Make sure you have CMake >= 3.12 before you do this when you use the Visual Studio generator.
 352 | set CMAKE_GENERATOR_TOOLSET_VERSION=14.27
 353 | set DISTUTILS_USE_SDK=1
 354 | for /f "usebackq tokens=*" %i in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -version [15^,17^) -products * -latest -property installationPath`) do call "%i\VC\Auxiliary\Build\vcvarsall.bat" x64 -vcvars_ver=%CMAKE_GENERATOR_TOOLSET_VERSION%
 355 | 
 356 | :: [Optional] If you want to override the CUDA host compiler
 357 | set CUDAHOSTCXX=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.27.29110\bin\HostX64\x64\cl.exe
 358 | 
 359 | python -m pip install --no-build-isolation -v -e .
 360 | ```
 361 | 
 362 | **Intel GPU builds**
 363 | 
 364 | In this mode PyTorch with Intel GPU support will be built.
 365 | 
 366 | Please make sure [the common prerequisites](#prerequisites) as well as [the prerequisites for Intel GPU](#intel-gpu-support) are properly installed and the environment variables are configured prior to starting the build. For build tool support, `Visual Studio 2022` is required.
 367 | 
 368 | Then PyTorch can be built with the command:
 369 | 
 370 | ```cmd
 371 | :: CMD Commands:
 372 | :: Set the CMAKE_PREFIX_PATH to help find corresponding packages
 373 | :: %CONDA_PREFIX% only works after `conda activate custom_env`
 374 | 
 375 | if defined CMAKE_PREFIX_PATH (
 376 |     set "CMAKE_PREFIX_PATH=%CONDA_PREFIX%\Library;%CMAKE_PREFIX_PATH%"
 377 | ) else (
 378 |     set "CMAKE_PREFIX_PATH=%CONDA_PREFIX%\Library"
 379 | )
 380 | 
 381 | python -m pip install --no-build-isolation -v -e .
 382 | ```
 383 | 
 384 | ##### Adjust Build Options (Optional)
 385 | 
 386 | You can adjust the configuration of cmake variables optionally (without building first), by doing
 387 | the following. For example, adjusting the pre-detected directories for CuDNN or BLAS can be done
 388 | with such a step.
 389 | 
 390 | On Linux
 391 | 
 392 | ```bash
 393 | export CMAKE_PREFIX_PATH="${CONDA_PREFIX:-'$(dirname $(which conda))/../'}:${CMAKE_PREFIX_PATH}"
 394 | CMAKE_ONLY=1 python setup.py build
 395 | ccmake build  # or cmake-gui build
 396 | ```
 397 | 
 398 | On macOS
 399 | 
 400 | ```bash
 401 | export CMAKE_PREFIX_PATH="${CONDA_PREFIX:-'$(dirname $(which conda))/../'}:${CMAKE_PREFIX_PATH}"
 402 | MACOSX_DEPLOYMENT_TARGET=11.0 CMAKE_ONLY=1 python setup.py build
 403 | ccmake build  # or cmake-gui build
 404 | ```
 405 | 
 406 | ### Docker Image
 407 | 
 408 | #### Using pre-built images
 409 | 
 410 | You can also pull a pre-built docker image from Docker Hub and run with docker v19.03+
 411 | 
 412 | ```bash
 413 | docker run --gpus all --rm -ti --ipc=host pytorch/pytorch:latest
 414 | ```
 415 | 
 416 | Please note that PyTorch uses shared memory to share data between processes, so if torch multiprocessing is used (e.g.
 417 | for multithreaded data loaders) the default shared memory segment size that container runs with is not enough, and you
 418 | should increase shared memory size either with `--ipc=host` or `--shm-size` command line options to `nvidia-docker run`.
 419 | 
 420 | #### Building the image yourself
 421 | 
 422 | **NOTE:** Must be built with a docker version > 18.06
 423 | 
 424 | The `Dockerfile` is supplied to build images with CUDA 11.1 support and cuDNN v8.
 425 | You can pass `PYTHON_VERSION=x.y` make variable to specify which Python version is to be used by Miniconda, or leave it
 426 | unset to use the default.
 427 | 
 428 | ```bash
 429 | make -f docker.Makefile
 430 | # images are tagged as docker.io/${your_docker_username}/pytorch
 431 | ```
 432 | 
 433 | You can also pass the `CMAKE_VARS="..."` environment variable to specify additional CMake variables to be passed to CMake during the build.
 434 | See [setup.py](./setup.py) for the list of available variables.
 435 | 
 436 | ```bash
 437 | make -f docker.Makefile
 438 | ```
 439 | 
 440 | ### Building the Documentation
 441 | 
 442 | To build documentation in various formats, you will need [Sphinx](http://www.sphinx-doc.org)
 443 | and the pytorch_sphinx_theme2.
 444 | 
 445 | Before you build the documentation locally, ensure `torch` is
 446 | installed in your environment. For small fixes, you can install the
 447 | nightly version as described in [Getting Started](https://pytorch.org/get-started/locally/).
 448 | 
 449 | For more complex fixes, such as adding a new module and docstrings for
 450 | the new module, you might need to install torch [from source](#from-source).
 451 | See [Docstring Guidelines](https://github.com/pytorch/pytorch/wiki/Docstring-Guidelines)
 452 | for docstring conventions.
 453 | 
 454 | ```bash
 455 | cd docs/
 456 | pip install -r requirements.txt
 457 | make html
 458 | make serve
 459 | ```
 460 | 
 461 | Run `make` to get a list of all available output formats.
 462 | 
 463 | If you get a katex error run `npm install katex`.  If it persists, try
 464 | `npm install -g katex`
 465 | 
 466 | > [!NOTE]
 467 | > If you installed `nodejs` with a different package manager (e.g.,
 468 | > `conda`) then `npm` will probably install a version of `katex` that is not
 469 | > compatible with your version of `nodejs` and doc builds will fail.
 470 | > A combination of versions that is known to work is `node@6.13.1` and
 471 | > `katex@0.13.18`. To install the latter with `npm` you can run
 472 | > ```npm install -g katex@0.13.18```
 473 | 
 474 | > [!NOTE]
 475 | > If you see a numpy incompatibility error, run:
 476 | > ```
 477 | > pip install 'numpy<2'
 478 | > ```
 479 | 
 480 | When you make changes to the dependencies run by CI, edit the
 481 | `.ci/docker/requirements-docs.txt` file.
 482 | 
 483 | #### Building a PDF
 484 | 
 485 | To compile a PDF of all PyTorch documentation, ensure you have
 486 | `texlive` and LaTeX installed. On macOS, you can install them using:
 487 | 
 488 | ```
 489 | brew install --cask mactex
 490 | ```
 491 | 
 492 | To create the PDF:
 493 | 
 494 | 1. Run:
 495 | 
 496 |    ```
 497 |    make latexpdf
 498 |    ```
 499 | 
 500 |    This will generate the necessary files in the `build/latex` directory.
 501 | 
 502 | 2. Navigate to this directory and execute:
 503 | 
 504 |    ```
 505 |    make LATEXOPTS="-interaction=nonstopmode"
 506 |    ```
 507 | 
 508 |    This will produce a `pytorch.pdf` with the desired content. Run this
 509 |    command one more time so that it generates the correct table
 510 |    of contents and index.
 511 | 
 512 | > [!NOTE]
 513 | > To view the Table of Contents, switch to the **Table of Contents**
 514 | > view in your PDF viewer.
 515 | 
 516 | 
 517 | ### Previous Versions
 518 | 
 519 | Installation instructions and binaries for previous PyTorch versions may be found
 520 | on [our website](https://pytorch.org/get-started/previous-versions).
 521 | 
 522 | 
 523 | ## Getting Started
 524 | 
 525 | Three pointers to get you started:
 526 | - [Tutorials: get you started with understanding and using PyTorch](https://pytorch.org/tutorials/)
 527 | - [Examples: easy to understand PyTorch code across all domains](https://github.com/pytorch/examples)
 528 | - [The API Reference](https://pytorch.org/docs/)
 529 | - [Glossary](https://github.com/pytorch/pytorch/blob/main/GLOSSARY.md)
 530 | 
 531 | ## Resources
 532 | 
 533 | * [PyTorch.org](https://pytorch.org/)
 534 | * [PyTorch Tutorials](https://pytorch.org/tutorials/)
 535 | * [PyTorch Examples](https://github.com/pytorch/examples)
 536 | * [PyTorch Models](https://pytorch.org/hub/)
 537 | * [Intro to Deep Learning with PyTorch from Udacity](https://www.udacity.com/course/deep-learning-pytorch--ud188)
 538 | * [Intro to Machine Learning with PyTorch from Udacity](https://www.udacity.com/course/intro-to-machine-learning-nanodegree--nd229)
 539 | * [Deep Neural Networks with PyTorch from Coursera](https://www.coursera.org/learn/deep-neural-networks-with-pytorch)
 540 | * [PyTorch Twitter](https://twitter.com/PyTorch)
 541 | * [PyTorch Blog](https://pytorch.org/blog/)
 542 | * [PyTorch YouTube](https://www.youtube.com/channel/UCWXI5YeOsh03QvJ59PMaXFw)
 543 | 
 544 | ## Communication
 545 | * Forums: Discuss implementations, research, etc. https://discuss.pytorch.org
 546 | * GitHub Issues: Bug reports, feature requests, install issues, RFCs, thoughts, etc.
 547 | * Slack: The [PyTorch Slack](https://pytorch.slack.com/) hosts a primary audience of moderate to experienced PyTorch users and developers for general chat, online discussions, collaboration, etc. If you are a beginner looking for help, the primary medium is [PyTorch Forums](https://discuss.pytorch.org). If you need a slack invite, please fill this form: https://goo.gl/forms/PP1AGvNHpSaJP8to1
 548 | * Newsletter: No-noise, a one-way email newsletter with important announcements about PyTorch. You can sign-up here: https://eepurl.com/cbG0rv
 549 | * Facebook Page: Important announcements about PyTorch. https://www.facebook.com/pytorch
 550 | * For brand guidelines, please visit our website at [pytorch.org](https://pytorch.org/)
 551 | 
 552 | ## Releases and Contributing
 553 | 
 554 | Typically, PyTorch has three minor releases a year. Please let us know if you encounter a bug by [filing an issue](https://github.com/pytorch/pytorch/issues).
 555 | 
 556 | We appreciate all contributions. If you are planning to contribute back bug-fixes, please do so without any further discussion.
 557 | 
 558 | If you plan to contribute new features, utility functions, or extensions to the core, please first open an issue and discuss the feature with us.
 559 | Sending a PR without discussion might end up resulting in a rejected PR because we might be taking the core in a different direction than you might be aware of.
 560 | 
 561 | To learn more about making a contribution to PyTorch, please see our [Contribution page](CONTRIBUTING.md). For more information about PyTorch releases, see [Release page](RELEASE.md).
 562 | 
 563 | ## The Team
 564 | 
 565 | PyTorch is a community-driven project with several skillful engineers and researchers contributing to it.
 566 | 
 567 | PyTorch is currently maintained by [Soumith Chintala](http://soumith.ch), [Gregory Chanan](https://github.com/gchanan), [Dmytro Dzhulgakov](https://github.com/dzhulgakov), [Edward Yang](https://github.com/ezyang), [Alban Desmaison](https://github.com/albanD), [Piotr Bialecki](https://github.com/ptrblck) and [Nikita Shulga](https://github.com/malfet) with major contributions coming from hundreds of talented individuals in various forms and means.
 568 | A non-exhaustive but growing list needs to mention: [Trevor Killeen](https://github.com/killeent), [Sasank Chilamkurthy](https://github.com/chsasank), [Sergey Zagoruyko](https://github.com/szagoruyko), [Adam Lerer](https://github.com/adamlerer), [Francisco Massa](https://github.com/fmassa), [Alykhan Tejani](https://github.com/alykhantejani), [Luca Antiga](https://github.com/lantiga), [Alban Desmaison](https://github.com/albanD), [Andreas Koepf](https://github.com/andreaskoepf), [James Bradbury](https://github.com/jekbradbury), [Zeming Lin](https://github.com/ebetica), [Yuandong Tian](https://github.com/yuandong-tian), [Guillaume Lample](https://github.com/glample), [Marat Dukhan](https://github.com/Maratyszcza), [Natalia Gimelshein](https://github.com/ngimel), [Christian Sarofeen](https://github.com/csarofeen), [Martin Raison](https://github.com/martinraison), [Edward Yang](https://github.com/ezyang), [Zachary Devito](https://github.com/zdevito). <!-- codespell:ignore -->
 569 | 
 570 | Note: This project is unrelated to [hughperkins/pytorch](https://github.com/hughperkins/pytorch) with the same name. Hugh is a valuable contributor to the Torch community and has helped with many things Torch and PyTorch.
 571 | 
 572 | ## License
 573 | 
 574 | PyTorch has a BSD-style license, as found in the [LICENSE](LICENSE) file.
```


---
## c10/cuda/README.md

```
   1 | c10/cuda is a core library with CUDA functionality.  It is distinguished
   2 | from c10 in that it links against the CUDA library, but like c10 it doesn't
   3 | contain any kernels, and consists solely of core functionality that is generally
   4 | useful when writing CUDA code; for example, C++ wrappers for the CUDA C API.
   5 | 
   6 | **Important notes for developers.** If you want to add files or functionality
   7 | to this folder, TAKE NOTE.  The code in this folder is very special,
   8 | because on our AMD GPU build, we transpile it into c10/hip to provide a
   9 | ROCm environment.  Thus, if you write:
  10 | 
  11 | ```
  12 | // c10/cuda/CUDAFoo.h
  13 | namespace c10 { namespace cuda {
  14 | 
  15 | void my_func();
  16 | 
  17 | }}
  18 | ```
  19 | 
  20 | this will get transpiled into:
  21 | 
  22 | 
  23 | ```
  24 | // c10/hip/HIPFoo.h
  25 | namespace c10 { namespace hip {
  26 | 
  27 | void my_func();
  28 | 
  29 | }}
  30 | ```
  31 | 
  32 | Thus, if you add new functionality to c10, you must also update `C10_MAPPINGS`
  33 | `torch/utils/hipify/cuda_to_hip_mappings.py` to transpile
  34 | occurrences of `cuda::my_func` to `hip::my_func`.  (At the moment,
  35 | we do NOT have a catch all `cuda::` to `hip::` namespace conversion,
  36 | as not all `cuda` namespaces are converted to `hip::`, even though
  37 | c10's are.)
  38 | 
  39 | Transpilation inside this folder is controlled by `CAFFE2_SPECIFIC_MAPPINGS`
  40 | (oddly enough.)  `C10_MAPPINGS` apply to ALL source files.
  41 | 
  42 | If you add a new directory to this folder, you MUST update both
  43 | c10/cuda/CMakeLists.txt and c10/hip/CMakeLists.txt
```
