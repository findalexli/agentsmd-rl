package selenium.tasktest;

import java.io.StringReader;
import java.lang.reflect.Method;
import java.time.Instant;
import java.util.Map;
import org.openqa.selenium.json.Json;
import org.openqa.selenium.json.JsonException;
import org.openqa.selenium.json.JsonInput;
import org.openqa.selenium.json.PropertySetting;

public class JsonTaskTest {

  public static void main(String[] args) throws Exception {
    if (args.length == 0) {
      System.err.println("usage: JsonTaskTest <method-name>");
      System.exit(2);
    }
    Method m = JsonTaskTest.class.getDeclaredMethod(args[0]);
    try {
      m.invoke(null);
      System.out.println("PASS: " + args[0]);
      System.exit(0);
    } catch (java.lang.reflect.InvocationTargetException e) {
      Throwable cause = e.getCause() != null ? e.getCause() : e;
      cause.printStackTrace();
      System.exit(1);
    } catch (Throwable t) {
      t.printStackTrace();
      System.exit(1);
    }
  }

  // ===== fail-to-pass: behavioral =====

  public static void parseVeryNegativeExponentialNotClampedToLong() {
    Object result = new Json().toType("-1e20", Number.class);
    if (!(result instanceof Number)) {
      throw new AssertionError("expected Number, got " + result);
    }
    double got = ((Number) result).doubleValue();
    double want = -1e20;
    // Long.MIN_VALUE is about -9.22e18 — the broken path returned that.
    // The fix returns the actual double value.
    if (Math.abs(got - want) > 1e10) {
      throw new AssertionError(
          "expected ~-1e20, got " + got + " (type=" + result.getClass().getName() + ")");
    }
  }

  public static void parseNegativeStringAsInstant() {
    Object result = new Json().toType("\"-1234\"", Instant.class);
    if (!(result instanceof Instant)) {
      throw new AssertionError("expected Instant, got " + result);
    }
    long ms = ((Instant) result).toEpochMilli();
    if (ms != -1234L) {
      throw new AssertionError("expected -1234 ms, got " + ms);
    }
  }

  public static void jsonInputHasNextEndMethod() throws Exception {
    Method m;
    try {
      m = JsonInput.class.getMethod("nextEnd");
    } catch (NoSuchMethodException e) {
      throw new AssertionError("JsonInput.nextEnd() is missing");
    }
    if (m.getReturnType() != void.class) {
      throw new AssertionError("nextEnd should return void, got " + m.getReturnType().getName());
    }
  }

  // Use reflection so the driver still compiles when nextEnd is absent on the
  // base commit; the existence test will surface the missing-method case
  // separately.
  private static void invokeNextEnd(JsonInput input) throws Throwable {
    Method m = JsonInput.class.getMethod("nextEnd");
    try {
      m.invoke(input);
    } catch (java.lang.reflect.InvocationTargetException ite) {
      throw ite.getCause();
    }
  }

  public static void nextEndRejectsRemainingTokens() throws Exception {
    try (JsonInput input = new Json().newInput(new StringReader("[1, 2, 3]"))) {
      input.beginArray();
      Number first = input.nextNumber();
      if (first.longValue() != 1L) {
        throw new AssertionError("expected first element 1, got " + first);
      }
      boolean threw = false;
      try {
        invokeNextEnd(input);
      } catch (NoSuchMethodException nsme) {
        throw new AssertionError("JsonInput.nextEnd() is missing");
      } catch (Throwable e) {
        threw = true;
      }
      if (!threw) {
        throw new AssertionError(
            "nextEnd() should throw when more tokens remain in the stream");
      }
    }
  }

  public static void nextEndAcceptsFullyConsumedInput() throws Exception {
    try (JsonInput input = new Json().newInput(new StringReader("42"))) {
      Number n = input.nextNumber();
      if (n.longValue() != 42L) {
        throw new AssertionError("expected 42, got " + n);
      }
      try {
        invokeNextEnd(input);
      } catch (NoSuchMethodException nsme) {
        throw new AssertionError("JsonInput.nextEnd() is missing");
      } catch (Throwable e) {
        throw new AssertionError("nextEnd() should not throw on consumed input: " + e);
      }
    }
  }

  public static void nextInstantIsDeprecatedForRemoval() throws Exception {
    Method m;
    try {
      m = JsonInput.class.getMethod("nextInstant");
    } catch (NoSuchMethodException e) {
      throw new AssertionError("JsonInput.nextInstant() is missing");
    }
    Deprecated d = m.getAnnotation(Deprecated.class);
    if (d == null) {
      throw new AssertionError("JsonInput.nextInstant should be marked @Deprecated");
    }
    if (!d.forRemoval()) {
      throw new AssertionError("JsonInput.nextInstant @Deprecated should set forRemoval=true");
    }
  }

  // ===== pass-to-pass: regression =====

  public static void canReadBoolean() {
    Object t = new Json().toType("true", Boolean.class);
    Object f = new Json().toType("false", Boolean.class);
    if (!Boolean.TRUE.equals(t)) throw new AssertionError("true expected, got " + t);
    if (!Boolean.FALSE.equals(f)) throw new AssertionError("false expected, got " + f);
  }

  public static void canReadIntegerAndDouble() {
    Object asInteger = new Json().toType("42", Integer.class);
    Object asDouble = new Json().toType("4.2e+1", Double.class);
    if (!Integer.valueOf(42).equals(asInteger)) {
      throw new AssertionError("expected 42, got " + asInteger);
    }
    if (!Double.valueOf(42.0).equals(asDouble)) {
      throw new AssertionError("expected 42.0, got " + asDouble);
    }
  }

  public static void canReadIsoInstantString() {
    Instant fixed = Instant.parse("2024-06-15T10:23:45.123456789Z");
    Object got = new Json().toType("\"" + fixed + "\"", Instant.class);
    if (!fixed.equals(got)) {
      throw new AssertionError("expected " + fixed + ", got " + got);
    }
  }

  public static void canRoundTripMap() {
    Map<String, Object> input = Map.of("name", "alice", "n", 7L);
    Json json = new Json();
    String encoded = json.toJson(input);
    Object decoded = json.toType(encoded, Json.MAP_TYPE);
    if (!(decoded instanceof Map)) {
      throw new AssertionError("expected Map, got " + decoded);
    }
    Map<?, ?> dm = (Map<?, ?>) decoded;
    if (!"alice".equals(dm.get("name"))) {
      throw new AssertionError("expected name=alice, got " + dm.get("name"));
    }
    Object n = dm.get("n");
    if (!(n instanceof Number) || ((Number) n).longValue() != 7L) {
      throw new AssertionError("expected n=7, got " + n);
    }
  }
}
