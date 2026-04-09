# Task: Cap Signatures in execute_transaction

The gRPC `execute_transaction` endpoint in `sui-rpc-api` currently accepts an unbounded number of `UserSignature`s. However, a transaction can only have at most two valid signatures: one for the sender and one for an optional sponsor.

## The Problem

Requests with more than two signatures should be rejected early with an `InvalidArgument` error, but currently they are accepted and processed unnecessarily.

## What You Need to Do

Add validation in the `execute_transaction` function in `crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/mod.rs` that:

1. Defines a constant `MAX_NUMBER_OF_SIGNATURES` set to `2` (one for sender, one for sponsor)
2. Checks if `request.signatures.len()` exceeds this limit **before** parsing the signatures
3. Returns a `FieldViolation` error with:
   - Field name: `"signatures"`
   - Description containing "exceeds the maximum allowed" and the actual counts
   - Reason: `ErrorReason::FieldInvalid`
4. Includes a comment explaining why the limit is 2

## Constraints

- The validation must occur **before** the existing signature parsing logic (early rejection)
- Use the existing error handling patterns in the file
- The code should compile without warnings or errors (`cargo check -p sui-rpc-api`)

## Files to Modify

- `crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/mod.rs`

## Testing

Your solution will be validated by:
- Checking that the `MAX_NUMBER_OF_SIGNATURES` constant exists and equals 2
- Verifying the validation logic is present and correctly positioned
- Confirming the error message format matches the specification
- Ensuring the code compiles successfully
