#!/bin/bash
set -e

cd /workspace/sui

# Check if already patched (idempotency check)
if grep -q "transfer_receive_object_cost_per_byte" crates/sui-protocol-config/src/lib.rs; then
    echo "Already patched"
    exit 0
fi

python3 << 'PYEOF'
import re

# 1. Update crates/sui-protocol-config/src/lib.rs
with open('crates/sui-protocol-config/src/lib.rs', 'r') as f:
    content = f.read()

# Add new fields after transfer_receive_object_cost_base
content = content.replace(
    'transfer_receive_object_cost_base: Option<u64>,',
    '''transfer_receive_object_cost_base: Option<u64>,
    transfer_receive_object_cost_per_byte: Option<u64>,
    transfer_receive_object_type_cost_per_byte: Option<u64>,''')

# Add None defaults after transfer_receive_object_cost_base: None
content = content.replace(
    'transfer_receive_object_cost_base: None,\n\n            // `tx_context`',
    '''transfer_receive_object_cost_base: None,
            transfer_receive_object_type_cost_per_byte: None,
            transfer_receive_object_cost_per_byte: None,

            // `tx_context`''')

# Add the config values for version 119 - must be set for ALL chains, not just Testnet
# The fields need to be set OUTSIDE the Testnet block so they apply to Unknown, Mainnet, and Testnet
content = content.replace(
    '''                    if chain == Chain::Testnet {
                        cfg.gasless_allowed_token_types = Some(vec![(TESTNET_USDC.to_string(), 0)]);
                    }''',
    '''                    if chain == Chain::Testnet {
                        cfg.gasless_allowed_token_types = Some(vec![(TESTNET_USDC.to_string(), 0)]);
                    }
                    cfg.transfer_receive_object_cost_per_byte = Some(1);
                    cfg.transfer_receive_object_type_cost_per_byte = Some(2);''')

with open('crates/sui-protocol-config/src/lib.rs', 'w') as f:
    f.write(content)

print("Updated lib.rs")

# 2. Update snapshot files
for snap_file in [
    'crates/sui-protocol-config/src/snapshots/sui_protocol_config__test__Mainnet_version_119.snap',
    'crates/sui-protocol-config/src/snapshots/sui_protocol_config__test__Testnet_version_119.snap',
    'crates/sui-protocol-config/src/snapshots/sui_protocol_config__test__version_119.snap'
]:
    try:
        with open(snap_file, 'r') as f:
            content = f.read()
        content = content.replace(
            'transfer_receive_object_cost_base: 52',
            '''transfer_receive_object_cost_base: 52
transfer_receive_object_cost_per_byte: 1
transfer_receive_object_type_cost_per_byte: 2''')
        with open(snap_file, 'w') as f:
            f.write(content)
        print(f"Updated {snap_file}")
    except FileNotFoundError:
        print(f"Warning: {snap_file} not found")

# 3. Update openrpc snapshot
try:
    with open('crates/sui-open-rpc/tests/snapshots/generate_spec__openrpc.snap.json', 'r') as f:
        content = f.read()
    content = content.replace(
        '"transfer_receive_object_cost_base": null,',
        '''"transfer_receive_object_cost_base": null,
                "transfer_receive_object_cost_per_byte": null,
                "transfer_receive_object_type_cost_per_byte": null,'''
    )
    with open('crates/sui-open-rpc/tests/snapshots/generate_spec__openrpc.snap.json', 'w') as f:
        f.write(content)
    print("Updated openrpc snapshot")
except FileNotFoundError:
    print("Warning: openrpc snapshot not found")

# 4. Update sui-execution/latest/sui-move-natives/src/lib.rs
with open('sui-execution/latest/sui-move-natives/src/lib.rs', 'r') as f:
    content = f.read()

# Add new fields to the TransferReceiveObjectInternalCostParams initialization
old_pattern = '''transfer_receive_object_internal_cost_base: protocol_config
                    .transfer_receive_object_cost_base_as_option()
                    .unwrap_or(0)
                    .into(),'''
new_replacement = '''transfer_receive_object_internal_cost_base: protocol_config
                    .transfer_receive_object_cost_base_as_option()
                    .unwrap_or(0)
                    .into(),
                transfer_receive_object_internal_cost_per_byte: protocol_config
                    .transfer_receive_object_cost_per_byte_as_option()
                    .unwrap_or(0)
                    .into(),
                transfer_receive_object_internal_type_cost_per_byte: protocol_config
                    .transfer_receive_object_type_cost_per_byte_as_option()
                    .unwrap_or(0)
                    .into(),'''
content = content.replace(old_pattern, new_replacement)

with open('sui-execution/latest/sui-move-natives/src/lib.rs', 'w') as f:
    f.write(content)

print("Updated lib.rs for natives")

# 5. Update transfer.rs
with open('sui-execution/latest/sui-move-natives/src/transfer.rs', 'r') as f:
    content = f.read()

# Add import
content = content.replace(
    'use move_vm_runtime::{\n    execution::Type,',
    'use move_vm_runtime::shared::views::{SizeConfig, ValueView};\nuse move_vm_runtime::{\n    execution::Type,')

# Add new fields to TransferReceiveObjectInternalCostParams (NOT replace the whole struct)
content = content.replace(
    '''pub struct TransferReceiveObjectInternalCostParams {
    pub transfer_receive_object_internal_cost_base: InternalGas,
}''',
    '''pub struct TransferReceiveObjectInternalCostParams {
    pub transfer_receive_object_internal_cost_base: InternalGas,
    pub transfer_receive_object_internal_cost_per_byte: InternalGas,
    pub transfer_receive_object_internal_type_cost_per_byte: InternalGas,
}''')

# Add type-based charging after getting child_ty
old_receive = '''let child_ty = ty_args.pop().unwrap();
    let child_receiver_sequence_number: SequenceNumber = pop_arg!(args, u64).into();'''
new_receive = '''let child_ty = ty_args.pop().unwrap();
    native_charge_gas_early_exit!(
        context,
        transfer_receive_object_internal_cost_params
            .transfer_receive_object_internal_type_cost_per_byte
            * u64::from(child_ty.size()?).into()
    );
    let child_receiver_sequence_number: SequenceNumber = pop_arg!(args, u64).into();'''
content = content.replace(old_receive, new_receive)

# Add size-based charging before returning
old_return = '''Ok(NativeResult::ok(context.gas_used(), smallvec![child]))
}'''
new_return = '''let child_size = child.abstract_memory_size(&SizeConfig {
        include_vector_size: true,
        traverse_references: true,
    })?;

    native_charge_gas_early_exit!(
        context,
        transfer_receive_object_internal_cost_params.transfer_receive_object_internal_cost_per_byte
            * u64::from(child_size).into()
    );

    Ok(NativeResult::ok(context.gas_used(), smallvec![child]))
}'''
content = content.replace(old_return, new_return)

with open('sui-execution/latest/sui-move-natives/src/transfer.rs', 'w') as f:
    f.write(content)

print("Updated transfer.rs")
print("All patches applied successfully!")
PYEOF

# Run cargo fmt to fix any formatting issues from the patches
cargo fmt

# Accept the insta snapshots so tests pass
cargo insta accept 2>/dev/null || echo "Insta accept completed or no pending snapshots"
