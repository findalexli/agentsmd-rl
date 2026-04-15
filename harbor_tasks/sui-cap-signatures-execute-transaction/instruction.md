# Task: Cap Signatures in Transaction Execution

The gRPC `execute_transaction` endpoint in `sui-rpc-api` currently accepts an unbounded number of `UserSignature`s. However, a Sui transaction can only have at most two valid signatures: one for the sender and one for an optional sponsor.

## The Problem

Requests with more than two signatures should be rejected early with an `InvalidArgument` error, but currently they are accepted and processed unnecessarily. This wastes resources on transactions that are fundamentally invalid.

## Requirements

Add validation that enforces a maximum of 2 signatures per transaction request, with the following specifications:

1. **Constant definition**: Define a constant named `MAX_NUMBER_OF_SIGNATURES` with value `2` of type `usize`, with a comment explaining the limit (one for sender, one for sponsor).

2. **Early validation**: Before parsing signatures, check if the request contains more than `MAX_NUMBER_OF_SIGNATURES`. The validation logic should compare `request.signatures.len()` against this limit.

3. **Error format**: When the limit is exceeded, return an error that:
   - Uses `FieldViolation::new("signatures")` to indicate which field is invalid
   - Includes a description containing the phrase "exceeds the maximum allowed" along with the actual and maximum counts
   - Uses `ErrorReason::FieldInvalid` as the error reason
   - Results in an `InvalidArgument` gRPC status code

4. **File location**: The validation should be added in `crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/mod.rs` within the transaction execution service.

## Constraints

- The validation must occur **before** any signature parsing happens (early rejection)
- Follow existing error handling patterns in the codebase
- The code must compile without warnings (`cargo check -p sui-rpc-api`)
- The code must be properly formatted (`cargo fmt`)

## Testing

Your solution will be validated by:
- Verifying the `MAX_NUMBER_OF_SIGNATURES` constant exists and equals 2
- Checking that validation logic using `request.signatures.len()` is present and positioned before signature parsing
- Confirming the error message contains "exceeds the maximum allowed"
- Ensuring `FieldViolation::new("signatures")` and `ErrorReason::FieldInvalid` are used
- Checking that the constant has an explanatory comment
- Verifying the code compiles successfully
