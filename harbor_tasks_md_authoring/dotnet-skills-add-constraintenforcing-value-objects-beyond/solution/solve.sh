#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "Value objects aren't just for identifiers. They're equally valuable for **enforc" "skills/csharp-coding-standards/value-objects-and-patterns.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/csharp-coding-standards/value-objects-and-patterns.md b/skills/csharp-coding-standards/value-objects-and-patterns.md
@@ -5,6 +5,7 @@ Full code examples for value objects and pattern matching in modern C#.
 ## Contents
 
 - [Value Objects as readonly record struct](#value-objects-as-readonly-record-struct)
+- [Constraint-Enforcing Value Objects](#constraint-enforcing-value-objects)
 - [No Implicit Conversions](#no-implicit-conversions)
 - [Pattern Matching (C# 8-12)](#pattern-matching-c-8-12)
 
@@ -56,25 +57,23 @@ public readonly record struct Money(decimal Amount, string Currency)
     public override string ToString() => $"{Amount:N2} {Currency}";
 }
 
-// Complex value object with factory pattern
+// Value object with input normalization
 public readonly record struct PhoneNumber
 {
     public string Value { get; }
 
-    private PhoneNumber(string value) => Value = value;
-
-    public static Result<PhoneNumber, string> Create(string input)
+    public PhoneNumber(string input)
     {
         if (string.IsNullOrWhiteSpace(input))
-            return Result<PhoneNumber, string>.Failure("Phone number cannot be empty");
+            throw new ArgumentException("Phone number cannot be empty", nameof(input));
 
         // Normalize: remove all non-digits
         var digits = new string(input.Where(char.IsDigit).ToArray());
 
-        if (digits.Length < 10 || digits.Length > 15)
-            return Result<PhoneNumber, string>.Failure("Phone number must be 10-15 digits");
+        if (digits.Length is < 10 or > 15)
+            throw new ArgumentException("Phone number must be 10-15 digits", nameof(input));
 
-        return Result<PhoneNumber, string>.Success(new PhoneNumber(digits));
+        Value = digits;
     }
 
     public override string ToString() => Value;
@@ -132,6 +131,136 @@ public readonly record struct Quantity(int Value, string Unit)
 - **Immutability**: `readonly` prevents accidental mutation
 - **Pattern matching**: Works seamlessly with switch expressions
 
+## Constraint-Enforcing Value Objects
+
+Value objects aren't just for identifiers. They're equally valuable for **enforcing domain constraints** on strings, numbers, and URIs — making illegal states unrepresentable at the type level.
+
+**Key principle: validate at construction, trust everywhere else.** Once you have an `AbsoluteUrl`, every consumer knows it's valid without re-checking.
+
+```csharp
+// AbsoluteUrl - enforces HTTP/HTTPS scheme constraints
+public readonly record struct AbsoluteUrl
+{
+    public Uri Value { get; }
+
+    public AbsoluteUrl(string uriString) : this(new Uri(uriString, UriKind.Absolute)) { }
+
+    public AbsoluteUrl(Uri value)
+    {
+        if (!value.IsAbsoluteUri)
+            throw new ArgumentException(
+                $"Value must be an absolute URL. Instead found [{value}]", nameof(value));
+        if (value.Scheme != Uri.UriSchemeHttp && value.Scheme != Uri.UriSchemeHttps)
+            throw new ArgumentException(
+                $"Value must be an HTTP or HTTPS URL. Instead found [{value.Scheme}]", nameof(value));
+        Value = value;
+    }
+
+    /// <summary>
+    /// Resolves a potentially relative URL against a base URL.
+    /// Handles Linux quirk where Uri.TryCreate("/path", UriKind.Absolute)
+    /// succeeds as file:///path.
+    /// </summary>
+    public static AbsoluteUrl FromRelative(string? url, AbsoluteUrl baseUrl)
+    {
+        if (string.IsNullOrEmpty(url))
+            throw new ArgumentException("URL cannot be null or empty", nameof(url));
+
+        if (Uri.TryCreate(url, UriKind.Absolute, out var absoluteUri) &&
+            (absoluteUri.Scheme == Uri.UriSchemeHttp || absoluteUri.Scheme == Uri.UriSchemeHttps))
+            return new AbsoluteUrl(absoluteUri);
+
+        return new AbsoluteUrl(new Uri(baseUrl.Value, url));
+    }
+
+    public override string ToString() => Value.ToString();
+}
+
+// NonEmptyString - prevents empty/whitespace strings from propagating
+public readonly record struct NonEmptyString
+{
+    public string Value { get; }
+
+    public NonEmptyString(string value)
+    {
+        if (string.IsNullOrWhiteSpace(value))
+            throw new ArgumentException("Value cannot be null or whitespace", nameof(value));
+        Value = value;
+    }
+
+    public override string ToString() => Value;
+}
+
+// EmailAddress - format validation at construction
+public readonly record struct EmailAddress
+{
+    public string Value { get; }
+
+    public EmailAddress(string value)
+    {
+        if (string.IsNullOrWhiteSpace(value))
+            throw new ArgumentException("Email cannot be empty", nameof(value));
+        if (!value.Contains('@') || !value.Contains('.'))
+            throw new ArgumentException($"Invalid email format: {value}", nameof(value));
+        Value = value.ToLowerInvariant();
+    }
+
+    public override string ToString() => Value;
+}
+
+// PositiveAmount - numeric range constraint
+public readonly record struct PositiveAmount
+{
+    public decimal Value { get; }
+
+    public PositiveAmount(decimal value)
+    {
+        if (value <= 0)
+            throw new ArgumentOutOfRangeException(nameof(value), "Amount must be positive");
+        Value = value;
+    }
+
+    public override string ToString() => Value.ToString("N2");
+}
+```
+
+**Why this matters:**
+- APIs like Slack Block Kit silently reject relative URLs with cryptic errors. Transactional email links break if they're relative. `AbsoluteUrl` makes the compiler prevent this.
+- Platform gotchas belong in the value object — e.g., Linux `Uri.TryCreate` treating `/path` as `file:///path` is handled once in `FromRelative`, not at every call site.
+
+### TypeConverter Support for Configuration Binding
+
+Add a `TypeConverter` so your value objects work with `IOptions<T>` and configuration binding:
+
+```csharp
+[TypeConverter(typeof(AbsoluteUrlTypeConverter))]
+public readonly record struct AbsoluteUrl
+{
+    // ... same as above
+}
+
+public sealed class AbsoluteUrlTypeConverter : TypeConverter
+{
+    public override bool CanConvertFrom(ITypeDescriptorContext? context, Type sourceType)
+        => sourceType == typeof(string) || base.CanConvertFrom(context, sourceType);
+
+    public override object? ConvertFrom(
+        ITypeDescriptorContext? context, CultureInfo? culture, object value)
+        => value is string s ? new AbsoluteUrl(s) : base.ConvertFrom(context, culture, value);
+}
+
+// Now this works with appsettings.json binding:
+public sealed class WebhookOptions
+{
+    public AbsoluteUrl CallbackUrl { get; set; }
+    public AbsoluteUrl HealthCheckUrl { get; set; }
+}
+
+// appsettings.json:
+// { "Webhook": { "CallbackUrl": "https://example.com/callback" } }
+services.Configure<WebhookOptions>(configuration.GetSection("Webhook"));
+```
+
 ## No Implicit Conversions
 
 **CRITICAL: NO implicit conversions.** Implicit operators defeat the purpose of value objects by allowing silent type coercion:
PATCH

echo "Gold patch applied."
