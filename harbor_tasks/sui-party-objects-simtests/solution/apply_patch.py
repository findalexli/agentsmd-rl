#!/usr/bin/env python3
"""Apply the PR changes to enable party object simtests under mainnet config and add deny list test."""

import re
import sys

def remove_mainnet_guards_from_party_tests():
    """Remove has_mainnet_protocol_config_override guards from party_objects_tests.rs."""
    file_path = "/workspace/sui/crates/sui-e2e-tests/tests/party_objects_tests.rs"

    with open(file_path, 'r') as f:
        content = f.read()

    # Pattern to match the guard block:
    #     if sui_simulator::has_mainnet_protocol_config_override() {
    #         return;
    #     }
    #
    guard_pattern = r'    if sui_simulator::has_mainnet_protocol_config_override\(\) \{\n        return;\n    \}\n\n'

    # Replace all occurrences
    new_content = re.sub(guard_pattern, '', content)

    # Count replacements
    count = len(re.findall(guard_pattern, content))
    print(f"Removed {count} mainnet protocol config override guards from party_objects_tests.rs")

    with open(file_path, 'w') as f:
        f.write(new_content)

    return True


def add_deny_list_test_to_stress_tests():
    """Add the new deny list test to per_epoch_config_stress_tests.rs."""
    file_path = "/workspace/sui/crates/sui-e2e-tests/tests/per_epoch_config_stress_tests.rs"

    with open(file_path, 'r') as f:
        content = f.read()

    # Update imports
    # 1. Change TypeTag import to include StructTag
    content = content.replace(
        'use move_core_types::language_storage::TypeTag;',
        'use move_core_types::language_storage::{StructTag, TypeTag};'
    )

    # 2. Add ExecutionErrorKind import after TransactionEffectsAPI
    content = content.replace(
        'use sui_types::effects::TransactionEffectsAPI;',
        'use sui_types::effects::TransactionEffectsAPI;\nuse sui_types::execution_status::ExecutionErrorKind;'
    )

    # 3. Update SUI_FRAMEWORK_PACKAGE_ID import to include SUI_FRAMEWORK_ADDRESS
    content = content.replace(
        'use sui_types::{SUI_DENY_LIST_OBJECT_ID, SUI_FRAMEWORK_PACKAGE_ID};',
        'use sui_types::{SUI_DENY_LIST_OBJECT_ID, SUI_FRAMEWORK_ADDRESS, SUI_FRAMEWORK_PACKAGE_ID};'
    )

    # Add the new test function after per_epoch_config_stress_test function
    new_test = '''/// Verify that the coin deny list is enforced for coins transferred via party_transfer.
#[sim_test]
async fn coin_deny_list_v2_party_owner_test() {
    let test_env = create_test_env().await;

    // Step 1: Add DENY_ADDRESS to the coin deny list.
    let gas_objects = test_env
        .test_cluster
        .wallet
        .get_all_gas_objects_owned_by_address(test_env.regulated_coin_owner)
        .await
        .unwrap();
    let deny_tx_data = test_env
        .test_cluster
        .test_transaction_builder_with_gas_object(test_env.regulated_coin_owner, gas_objects[0])
        .await
        .move_call_with_type_args(
            SUI_FRAMEWORK_PACKAGE_ID,
            "coin",
            "deny_list_v2_add",
            vec![test_env.regulated_coin_type.clone()],
            vec![
                CallArg::Object(ObjectArg::SharedObject {
                    id: SUI_DENY_LIST_OBJECT_ID,
                    initial_shared_version: test_env.deny_list_object_init_version,
                    mutability: SharedObjectMutability::Mutable,
                }),
                CallArg::Object(ObjectArg::ImmOrOwnedObject(
                    test_env.get_latest_object_ref(&test_env.deny_cap_id).await,
                )),
                CallArg::Pure(bcs::to_bytes(&DENY_ADDRESS).unwrap()),
            ],
        )
        .build();
    let deny_effects = test_env
        .test_cluster
        .sign_and_execute_transaction(&deny_tx_data)
        .await
        .effects;
    assert!(
        deny_effects.status().is_ok(),
        "Deny list add should succeed"
    );

    // Step 2: Advance epoch so the deny list change takes effect.
    test_env.test_cluster.trigger_reconfiguration().await;

    // Step 3: Build a PTB that splits a regulated coin and does public_party_transfer
    // to the denied address (creating a ConsensusAddressOwner coin).
    let gas_objects = test_env
        .test_cluster
        .wallet
        .get_all_gas_objects_owned_by_address(test_env.regulated_coin_owner)
        .await
        .unwrap();
    let mut tx_builder = test_env
        .test_cluster
        .test_transaction_builder_with_gas_object(test_env.regulated_coin_owner, gas_objects[0])
        .await;
    {
        let pt_builder = tx_builder.ptb_builder_mut();

        let coin_input = pt_builder
            .obj(ObjectArg::ImmOrOwnedObject(
                test_env
                    .get_latest_object_ref(&test_env.regulated_coin_id)
                    .await,
            ))
            .unwrap();
        let amount_input = pt_builder.pure(1u64).unwrap();
        let split_coin = pt_builder.programmable_move_call(
            SUI_FRAMEWORK_PACKAGE_ID,
            ident_str!("coin").to_owned(),
            ident_str!("split").to_owned(),
            vec![test_env.regulated_coin_type.clone()],
            vec![coin_input, amount_input],
        );

        let addr_input = pt_builder.pure(DENY_ADDRESS).unwrap();
        let party = pt_builder.programmable_move_call(
            SUI_FRAMEWORK_PACKAGE_ID,
            ident_str!("party").to_owned(),
            ident_str!("single_owner").to_owned(),
            vec![],
            vec![addr_input],
        );

        let coin_type_tag = TypeTag::Struct(Box::new(StructTag {
            address: SUI_FRAMEWORK_ADDRESS,
            module: ident_str!("coin").to_owned(),
            name: ident_str!("Coin").to_owned(),
            type_params: vec![test_env.regulated_coin_type.clone()],
        }));
        pt_builder.programmable_move_call(
            SUI_FRAMEWORK_PACKAGE_ID,
            ident_str!("transfer").to_owned(),
            ident_str!("public_party_transfer").to_owned(),
            vec![coin_type_tag],
            vec![split_coin, party],
        );
    }
    let transfer_tx_data = tx_builder.build();

    // Step 4: Execute and verify it fails with AddressDeniedForCoin.
    let tx = test_env
        .test_cluster
        .sign_transaction(&transfer_tx_data)
        .await;
    let response = test_env
        .test_cluster
        .wallet
        .execute_transaction_may_fail(tx)
        .await
        .unwrap();
    let effects = response.effects;
    assert!(
        effects.status().is_err(),
        "Transaction should fail due to coin deny list for party owner"
    );
    let (error_kind, _command) = effects.into_status().unwrap_err();
    assert!(
        matches!(
            &error_kind,
            ExecutionErrorKind::AddressDeniedForCoin { address, .. }
            if *address == DENY_ADDRESS
        ),
        "Expected AddressDeniedForCoin for {DENY_ADDRESS}, got: {error_kind:?}"
    );
}
'''

    # Find the end of per_epoch_config_stress_test and add the new test after it
    # The function ends with ".unwrap().unwrap();\n}\n\nasync fn run_thread"
    # Find the position of "async fn run_thread" and insert before it
    run_thread_pos = content.find('async fn run_thread')
    if run_thread_pos != -1:
        # Insert before run_thread - add trailing newline to match format
        content = content[:run_thread_pos] + new_test + content[run_thread_pos:]
        print("Added coin_deny_list_v2_party_owner_test to per_epoch_config_stress_tests.rs")
    else:
        print("Could not find run_thread function")
        return False

    with open(file_path, 'w') as f:
        f.write(content)

    return True


def main():
    print("Applying patch to enable party object simtests under mainnet config...")

    try:
        if not remove_mainnet_guards_from_party_tests():
            print("Failed to remove mainnet guards")
            return 1

        if not add_deny_list_test_to_stress_tests():
            print("Failed to add deny list test")
            return 1

        print("Patch applied successfully")
        return 0
    except Exception as e:
        print(f"Error applying patch: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
