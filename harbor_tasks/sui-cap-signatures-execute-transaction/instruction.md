# Task: Cap Signatures in Transaction Execution

The gRPC `execute_transaction` endpoint in `crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/mod.rs` currently accepts an unbounded number of `UserSignature`s. However, a Sui transaction can only have at most two valid signatures: one for the sender and one for an optional sponsor.

## The Problem

Requests with more than two signatures should be rejected early with an `InvalidArgument` gRPC error, but currently they are accepted and processed unnecessarily. This wastes resources on transactions that are fundamentally invalid.

## Requirements

Add validation that enforces a maximum of 2 signatures per transaction request:

1. **Early validation**: Before parsing signatures, check if the request contains too many signatures and return an error if so
2. **Error format**: When the limit is exceeded, return an `InvalidArgument` gRPC error with:
   - A `FieldViolation` on the `signatures` field
   - The error reason set to `FieldInvalid`
   - A message containing the substring "exceeds the maximum allowed"
3. **Constant definition**: Define a constant named `MAX_NUMBER_OF_SIGNATURES` with value `2` (with a comment explaining it covers one sender and one sponsor)
4. **Code quality**: The code must compile without warnings and be properly formatted

## Constraints

- The validation must occur **before** any signature parsing happens (early rejection)
- Follow existing error handling patterns in the codebase
- The code must compile without warnings (`cargo check -p sui-rpc-api`)
- The code must be properly formatted (`cargo fmt`)

## Testing

Your solution will be validated by:
- Verifying the code compiles successfully
- Checking that validation logic is present and positioned before signature parsing
- Confirming proper error handling is implemented
- Ensuring the code is properly formatted

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
