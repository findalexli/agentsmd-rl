#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "For expected errors, use a **domain-specific result type** instead of exceptions" "skills/csharp-coding-standards/composition-and-error-handling.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/csharp-coding-standards/composition-and-error-handling.md b/skills/csharp-coding-standards/composition-and-error-handling.md
@@ -5,7 +5,7 @@ Composition over inheritance, Result type pattern, and testing patterns for mode
 ## Contents
 
 - [Composition Over Inheritance](#composition-over-inheritance)
-- [Result Type Pattern (Railway-Oriented Programming)](#result-type-pattern-railway-oriented-programming)
+- [Result Type Pattern](#result-type-pattern)
 - [Testing Patterns](#testing-patterns)
 
 ## Composition Over Inheritance
@@ -112,107 +112,82 @@ public record PaymentMethod
 - Library integration (e.g., custom exceptions inheriting from `Exception`)
 - **These should be rare cases in your application code**
 
-## Result Type Pattern (Railway-Oriented Programming)
+## Result Type Pattern
 
-For expected errors, use a `Result<T, TError>` type instead of exceptions.
+For expected errors, use a **domain-specific result type** instead of exceptions. Don't build a generic `Result<T>` — each operation knows what success and failure look like, so let the result type reflect that. Use sealed records with factory methods and enum error codes.
 
 ```csharp
-// Simple Result type as readonly record struct
-public readonly record struct Result<TValue, TError>
+// Enum for error classification - type-safe and switchable
+public enum OrderErrorCode
 {
-    private readonly TValue? _value;
-    private readonly TError? _error;
-    private readonly bool _isSuccess;
+    ValidationError,
+    InsufficientInventory,
+    NotFound
+}
 
-    private Result(TValue value)
-    {
-        _value = value;
-        _error = default;
-        _isSuccess = true;
-    }
+// Domain-specific result type - sealed record with factory methods
+public sealed record CreateOrderResult
+{
+    public bool IsSuccess { get; private init; }
+    public Order? Order { get; private init; }
+    public OrderErrorCode? ErrorCode { get; private init; }
+    public string? ErrorMessage { get; private init; }
 
-    private Result(TError error)
+    public static CreateOrderResult Success(Order order) => new()
     {
-        _value = default;
-        _error = error;
-        _isSuccess = false;
-    }
-
-    public bool IsSuccess => _isSuccess;
-    public bool IsFailure => !_isSuccess;
-
-    public TValue Value => _isSuccess
-        ? _value!
-        : throw new InvalidOperationException("Cannot access Value of a failed result");
-
-    public TError Error => !_isSuccess
-        ? _error!
-        : throw new InvalidOperationException("Cannot access Error of a successful result");
-
-    public static Result<TValue, TError> Success(TValue value) => new(value);
-    public static Result<TValue, TError> Failure(TError error) => new(error);
-
-    public Result<TOut, TError> Map<TOut>(Func<TValue, TOut> mapper)
-        => _isSuccess
-            ? Result<TOut, TError>.Success(mapper(_value!))
-            : Result<TOut, TError>.Failure(_error!);
-
-    public Result<TOut, TError> Bind<TOut>(Func<TValue, Result<TOut, TError>> binder)
-        => _isSuccess ? binder(_value!) : Result<TOut, TError>.Failure(_error!);
-
-    public TValue GetValueOr(TValue defaultValue)
-        => _isSuccess ? _value! : defaultValue;
+        IsSuccess = true,
+        Order = order
+    };
 
-    public TResult Match<TResult>(
-        Func<TValue, TResult> onSuccess,
-        Func<TError, TResult> onFailure)
-        => _isSuccess ? onSuccess(_value!) : onFailure(_error!);
+    public static CreateOrderResult Failed(OrderErrorCode code, string message) => new()
+    {
+        IsSuccess = false,
+        ErrorCode = code,
+        ErrorMessage = message
+    };
 }
 
-// Error type as readonly record struct
-public readonly record struct OrderError(string Code, string Message);
-
 // Usage example
 public sealed class OrderService(IOrderRepository repository)
 {
-    public async Task<Result<Order, OrderError>> CreateOrderAsync(
+    public async Task<CreateOrderResult> CreateOrderAsync(
         CreateOrderRequest request,
         CancellationToken cancellationToken)
     {
-        // Validate
-        var validationResult = ValidateRequest(request);
-        if (validationResult.IsFailure)
-            return Result<Order, OrderError>.Failure(validationResult.Error);
+        if (!IsValid(request))
+            return CreateOrderResult.Failed(
+                OrderErrorCode.ValidationError, "Invalid order request");
 
-        // Check inventory
-        var inventoryResult = await CheckInventoryAsync(request.Items, cancellationToken);
-        if (inventoryResult.IsFailure)
-            return Result<Order, OrderError>.Failure(inventoryResult.Error);
+        if (!await HasInventoryAsync(request.Items, cancellationToken))
+            return CreateOrderResult.Failed(
+                OrderErrorCode.InsufficientInventory, "Items out of stock");
 
-        // Create order
         var order = new Order(
             OrderId.New(),
             new CustomerId(request.CustomerId),
             request.Items);
 
         await repository.SaveAsync(order, cancellationToken);
 
-        return Result<Order, OrderError>.Success(order);
+        return CreateOrderResult.Success(order);
     }
 
-    // Pattern matching on Result
-    public IActionResult MapToActionResult(Result<Order, OrderError> result)
+    // Map result to HTTP response - switch on enum error codes
+    public IActionResult MapToActionResult(CreateOrderResult result)
     {
-        return result.Match(
-            onSuccess: order => new OkObjectResult(order),
-            onFailure: error => error.Code switch
-            {
-                "VALIDATION_ERROR" => new BadRequestObjectResult(error.Message),
-                "INSUFFICIENT_INVENTORY" => new ConflictObjectResult(error.Message),
-                "NOT_FOUND" => new NotFoundObjectResult(error.Message),
-                _ => new ObjectResult(error.Message) { StatusCode = 500 }
-            }
-        );
+        if (result.IsSuccess)
+            return new OkObjectResult(result.Order);
+
+        return result.ErrorCode switch
+        {
+            OrderErrorCode.ValidationError =>
+                new BadRequestObjectResult(new { error = result.ErrorMessage }),
+            OrderErrorCode.InsufficientInventory =>
+                new ConflictObjectResult(new { error = result.ErrorMessage }),
+            OrderErrorCode.NotFound =>
+                new NotFoundObjectResult(new { error = result.ErrorMessage }),
+            _ => new ObjectResult(new { error = result.ErrorMessage }) { StatusCode = 500 }
+        };
     }
 }
 ```
PATCH

echo "Gold patch applied."
