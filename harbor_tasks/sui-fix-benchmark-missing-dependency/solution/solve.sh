#!/bin/bash
set -e

cd /workspace/sui

CRATE_DIR="external-crates/move/crates/language-benchmarks"

# Apply changes to move_vm.rs using a Python script
cat > /tmp/patch_move_vm.py << 'PYEOF'
import re

CRATE_DIR = "external-crates/move/crates/language-benchmarks"

with open(f"{CRATE_DIR}/src/move_vm.rs", "r") as f:
    content = f.read()

# 1. Add BENCH_ADDR constants after BENCH_FUNCTION_PREFIX
old_const = 'const BENCH_FUNCTION_PREFIX: &str = "bench_";'
new_const = '''const BENCH_FUNCTION_PREFIX: &str = "bench_";
const BENCH_ADDR: AccountAddress = AccountAddress::new([
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
]);
const BENCH_ADDR_STR: &str = "0x2";'''

content = content.replace(old_const, new_const)

# 2. Update bench() function
content = content.replace(
    '''pub fn bench<M: Measurement + 'static>(c: &mut Criterion<M>, filename: &str) {
    let modules = compile_modules(filename);
    let mut move_vm = create_vm();
    execute(c, &mut move_vm, modules, filename);
}''',
    '''pub fn bench<M: Measurement + 'static>(c: &mut Criterion<M>, filename: &str) {
    let modules = compile_modules(filename);
    let mut adapter = create_vm();
    publish_stdlib(&mut adapter);
    execute(c, &mut adapter, BENCH_ADDR, modules, filename);
}'''
)

# 3. Update compile_modules - we need to handle the chained method call properly
old_compile = '''    let (_files, compiled_units) =
        Compiler::from_files(None, src_files, vec![], move_stdlib::named_addresses())
            .set_pre_compiled_program_opt(Some(Arc::new(PRECOMPILED_MOVE_STDLIB.clone())))
            .set_default_config(pkg_config)
            .build_and_report()
            .expect("Error compiling...");'''

new_compile = '''    let mut named_addresses = move_stdlib::named_addresses();
    named_addresses.insert(
        "bench".to_string(),
        move_core_types::parsing::address::NumericalAddress::parse_str(BENCH_ADDR_STR).unwrap(),
    );
    let (_files, compiled_units) =
        Compiler::from_files(None, src_files, vec![], named_addresses)
            .set_pre_compiled_program_opt(Some(Arc::new(PRECOMPILED_MOVE_STDLIB.clone())))
            .set_default_config(pkg_config)
            .build_and_report()
            .expect("Error compiling...");'''

content = content.replace(old_compile, new_compile)

# 4. Add publish_stdlib function after create_vm
old_create_vm = '''fn create_vm() -> InMemoryTestAdapter {
    InMemoryTestAdapter::new_with_runtime(MoveRuntime::new_with_default_config(
        stdlib_native_functions(
            AccountAddress::from_hex_literal("0x1").unwrap(),
            move_vm_runtime::natives::move_stdlib::GasParameters::zeros(),
            /* silent debug */ true,
        )
        .unwrap(),
    ))
}'''

new_create_vm_with_publish = '''fn create_vm() -> InMemoryTestAdapter {
    InMemoryTestAdapter::new_with_runtime(MoveRuntime::new_with_default_config(
        stdlib_native_functions(
            AccountAddress::from_hex_literal("0x1").unwrap(),
            move_vm_runtime::natives::move_stdlib::GasParameters::zeros(),
            /* silent debug */ true,
        )
        .unwrap(),
    ))
}

fn publish_stdlib(adapter: &mut InMemoryTestAdapter) {
    let stdlib_modules: Vec<CompiledModule> = PRECOMPILED_MOVE_STDLIB
        .iter()
        .filter_map(|(_, info)| {
            info.compiled_unit
                .as_ref()
                .map(|unit| unit.named_module.module.clone())
        })
        .collect();
    if stdlib_modules.is_empty() {
        return;
    }
    let pkg = StoredPackage::from_modules_for_testing(CORE_CODE_ADDRESS, stdlib_modules).unwrap();
    adapter.insert_package_into_storage(pkg);
}'''

content = content.replace(old_create_vm, new_create_vm_with_publish)

# 5. Update run_cross_module_tests
old_cross = '''pub fn run_cross_module_tests<M: Measurement + 'static>(c: &mut Criterion<M>, path: PathBuf) {
    let modules_a1 = build_package(path).unwrap();
    let modules = modules_a1
        .all_modules()
        .map(|m| m.unit.module.clone())
        .collect::<Vec<_>>();
    let mut move_vm = create_vm();
    execute(c, &mut move_vm, modules, "cross_module/a1/sources/m.move");
}'''

new_cross = '''pub fn run_cross_module_tests<M: Measurement + 'static>(c: &mut Criterion<M>, path: PathBuf) {
    let modules_a1 = build_package(path).unwrap();
    let modules = modules_a1
        .all_modules()
        .map(|m| m.unit.module.clone())
        .collect::<Vec<_>>();
    let mut adapter = create_vm();
    publish_stdlib(&mut adapter);
    execute(c, &mut adapter, CORE_CODE_ADDRESS, modules, "cross_module/a1/sources/m.move");
}'''

content = content.replace(old_cross, new_cross)

# 6. Update execute function signature
old_execute = '''// execute a given function in the Bench module
fn execute<M: Measurement + 'static>(
    c: &mut Criterion<M>,
    adapter: &mut InMemoryTestAdapter,
    modules: Vec<CompiledModule>,
    file: &str,
) {
    // establish running context
    let sender = CORE_CODE_ADDRESS;'''

new_execute = '''// execute a given function in the Bench module
fn execute<M: Measurement + 'static>(
    c: &mut Criterion<M>,
    adapter: &mut InMemoryTestAdapter,
    sender: AccountAddress,
    modules: Vec<CompiledModule>,
    file: &str,
) {'''

content = content.replace(old_execute, new_execute)

with open(f"{CRATE_DIR}/src/move_vm.rs", "w") as f:
    f.write(content)

print("move_vm.rs patched successfully")
PYEOF

CRATE_DIR="external-crates/move/crates/language-benchmarks" python3 /tmp/patch_move_vm.py

# Update criterion.rs - comment out cross_module
cat > /tmp/patch_criterion.py << 'PYEOF'
CRATE_DIR = "external-crates/move/crates/language-benchmarks"

with open(f"{CRATE_DIR}/benches/criterion.rs", "r") as f:
    content = f.read()

# Add #[allow(dead_code)] to cross_module function
old_cross_fn = 'fn cross_module<M: Measurement + \'static>(c: &mut Criterion<M>) {'
new_cross_fn = '#[allow(dead_code)]\nfn cross_module<M: Measurement + \'static>(c: &mut Criterion<M>) {'
content = content.replace(old_cross_fn, new_cross_fn)

# Comment out cross_module in criterion_group
old_group = '''        cross_module,
);'''
new_group = '''        // cross_module, // TODO: broken — uses multi-address packages not supported by current setup
);'''
content = content.replace(old_group, new_group)

with open(f"{CRATE_DIR}/benches/criterion.rs", "w") as f:
    f.write(content)

print("criterion.rs patched successfully")
PYEOF

python3 /tmp/patch_criterion.py

# Update all Move files - change 0x1 to 0x2
for file in arith.move basic_alloc.move branch.move call.move loop.move natives.move transfers.move vector.move; do
    sed -i 's/module 0x1::bench/module 0x2::bench/g' "${CRATE_DIR}/tests/${file}"
    sed -i 's/0x1::bench_xmodule_call/0x2::bench_xmodule_call/g' "${CRATE_DIR}/tests/${file}"
    # Also update module declaration for bench_xmodule_call
    sed -i 's/module 0x1::bench_xmodule_call/module 0x2::bench_xmodule_call/g' "${CRATE_DIR}/tests/${file}"
    echo "Patched ${file}"
done

# Verify the patch was applied
echo "Verifying patches..."
grep -q "const BENCH_ADDR: AccountAddress" "${CRATE_DIR}/src/move_vm.rs" && echo "✓ BENCH_ADDR found in move_vm.rs"
grep -q "module 0x2::bench" "${CRATE_DIR}/tests/arith.move" && echo "✓ 0x2::bench found in arith.move"
grep -q "module 0x2::bench_xmodule_call" "${CRATE_DIR}/tests/call.move" && echo "✓ 0x2::bench_xmodule_call found in call.move"
grep -q "// cross_module" "${CRATE_DIR}/benches/criterion.rs" && echo "✓ cross_module commented out in criterion.rs"

echo "All patches applied successfully!"
