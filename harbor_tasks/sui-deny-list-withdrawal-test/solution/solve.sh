#!/bin/bash
set -e

cd /workspace/sui

# Apply the patch to add the denied address withdrawal test
cat <<'PATCH' | git apply -
diff --git a/crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.move b/crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.move
index 64180c4f6a81..ac6e5ec4ba6b 100644
--- a/crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.move
+++ b/crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.move
@@ -55,6 +55,8 @@ public fun split_to_balance(
 //> 0: test::regulated_coin::split_to_balance(Input(0), Input(1));
 //> 1: sui::balance::send_funds<test::regulated_coin::REGULATED_COIN>(Result(0), Input(2));

+//# create-checkpoint
+
 //# advance-epoch

 // After epoch change, the deny list should block the recipient.
@@ -62,6 +64,11 @@ public fun split_to_balance(
 //> 0: test::regulated_coin::split_to_balance(Input(0), Input(1));
 //> 1: sui::balance::send_funds<test::regulated_coin::REGULATED_COIN>(Result(0), Input(2));

+//# programmable --sender B --inputs withdraw<sui::balance::Balance<test::regulated_coin::REGULATED_COIN>>(1) @A
+// withdraw funds from denied account B
+//> 0: sui::balance::redeem_funds(Input(0));
+//> 1: sui::balance::send_funds<test::regulated_coin::REGULATED_COIN>(Result(0), Input(1));
+
 // Undeny account B.
 //# run sui::coin::deny_list_v2_remove --args object(0x403) object(1,3) @B --type-args test::regulated_coin::REGULATED_COIN --sender A

diff --git a/crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.snap b/crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.snap
index ba84d38b57bd..6c244b8b3e73 100644
--- a/crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.snap
+++ b/crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.snap
@@ -1,8 +1,7 @@
 ---
 source: external-crates/move/crates/move-transactional-test-runner/src/framework.rs
-assertion_line: 908
 ---
-processed 11 tasks
+processed 13 tasks

 init:
 A: object(0,0), B: object(0,1)
@@ -40,35 +39,46 @@ unchanged_shared: 0x000000000000000000000000000000000000000000000000000000000000
 accumulators_written: (object(2,0), B, sui::balance::Balance<test::regulated_coin::REGULATED_COIN>, Merge, 1)
 gas summary: computation_cost: 1000000, storage_cost: 2462400,  storage_rebate: 2437776, non_refundable_storage_fee: 24624

-task 5, lines 58-60:
+task 5, line 58:
+//# create-checkpoint
+Checkpoint created: 1
+
+task 6, lines 60-62:
 //# advance-epoch
 Epoch advanced: 1

-task 6, lines 61-65:
+task 7, lines 63-65:
 //# programmable --sender A --inputs object(1,1) 1 @B
 //> 0: test::regulated_coin::split_to_balance(Input(0), Input(1));
 //> 1: sui::balance::send_funds<test::regulated_coin::REGULATED_COIN>(Result(0), Input(2));
-// Undeny account B.
 Error: Transaction Effects Status: Address B is denied for coin test::regulated_coin::REGULATED_COIN
 Execution Error: ExecutionError: ExecutionError { inner: ExecutionErrorInner { kind: AddressDeniedForCoin { address: B, coin_type: "test::regulated_coin::REGULATED_COIN" }, source: None, command: None } }

-task 7, lines 66-68:
+task 8, lines 67-72:
+//# programmable --sender B --inputs withdraw<sui::balance::Balance<test::regulated_coin::REGULATED_COIN>>(1) @A
+// withdraw funds from denied account B
+//> 0: sui::balance::redeem_funds(Input(0));
+//> 1: sui::balance::send_funds<test::regulated_coin::REGULATED_COIN>(Result(0), Input(1));
+// Undeny account B.
+Error: Error checking transaction input objects: Address @B is denied for coin object(1,0)::regulated_coin::REGULATED_COIN
+
+task 9, lines 73-75:
 //# run sui::coin::deny_list_v2_remove --args object(0x403) object(1,3) @B --type-args test::regulated_coin::REGULATED_COIN --sender A
 mutated: 0x0000000000000000000000000000000000000000000000000000000000000403, object(0,0), object(1,3), object(3,1)
 gas summary: computation_cost: 1000000, storage_cost: 6862800,  storage_rebate: 6794172, non_refundable_storage_fee: 68628

-task 8, lines 69-71:
+task 10, lines 76-78:
 //# programmable --sender A --inputs object(1,1) 1 @B
 //> 0: test::regulated_coin::split_to_balance(Input(0), Input(1));
 //> 1: sui::balance::send_funds<test::regulated_coin::REGULATED_COIN>(Result(0), Input(2));
 Error: Transaction Effects Status: Address B is denied for coin test::regulated_coin::REGULATED_COIN
 Execution Error: ExecutionError: ExecutionError { inner: ExecutionErrorInner { kind: AddressDeniedForCoin { address: B, coin_type: "test::regulated_coin::REGULATED_COIN" }, source: None, command: None } }

-task 9, lines 73-75:
+task 11, lines 80-82:
 //# advance-epoch
 Epoch advanced: 2

-task 10, lines 76-78:
+task 12, lines 83-85:
 //# programmable --sender A --inputs object(1,1) 1 @B
 //> 0: test::regulated_coin::split_to_balance(Input(0), Input(1));
 //> 1: sui::balance::send_funds<test::regulated_coin::REGULATED_COIN>(Result(0), Input(2));
PATCH

# Idempotency check: verify the distinctive line from the patch exists
grep -q "withdraw funds from denied account B" crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.move
echo "Patch applied successfully"
