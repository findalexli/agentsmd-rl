FROM eclipse-temurin:17.0.13_11-jdk-jammy

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

# Clone selenium at the base commit, sparse-checkout only what we need.
RUN git clone --filter=blob:none --no-checkout https://github.com/SeleniumHQ/selenium.git /workspace/selenium && \
    cd /workspace/selenium && \
    git sparse-checkout init --cone && \
    git sparse-checkout set java/src/org/openqa/selenium/bidi java/src/org/openqa/selenium/internal && \
    git checkout 658c69f13ab531cfeb982471f25fd435777b91d9

# Stubs let us compile BiDi.java in isolation without pulling all of selenium's
# transitive deps (jetty, gson, websocket libs, etc). They reproduce only the
# surface area BiDi.java touches.
RUN mkdir -p /workspace/stubs/org/openqa/selenium/bidi /workspace/stubs/org/openqa/selenium/internal

RUN cat > /workspace/stubs/org/openqa/selenium/internal/Require.java <<'JAVA'
package org.openqa.selenium.internal;

public class Require {
  public static <T> T nonNull(String name, T value) {
    if (value == null) {
      throw new NullPointerException(name + " must not be null");
    }
    return value;
  }
}
JAVA

RUN cat > /workspace/stubs/org/openqa/selenium/bidi/Connection.java <<'JAVA'
package org.openqa.selenium.bidi;

import java.io.Closeable;
import java.time.Duration;
import java.util.function.Consumer;

public class Connection implements Closeable {
  public Connection() {}

  public <X> X sendAndWait(Command<X> command, Duration timeout) {
    return null;
  }

  public <X> long addListener(Event<X> event, Consumer<X> handler) {
    return 0L;
  }

  public <X> boolean isEventSubscribed(Event<X> event) {
    return false;
  }

  public <X> void clearListener(Event<X> event) {}

  public void removeListener(long id) {}

  public void clearListeners() {}

  @Override
  public void close() {}
}
JAVA

RUN cat > /workspace/stubs/org/openqa/selenium/bidi/Command.java <<'JAVA'
package org.openqa.selenium.bidi;

import java.util.Map;
import java.util.function.Function;

public class Command<X> {
  public Command(String method, Map<String, Object> params) {}
  public Command(String method, Map<String, Object> params, Class<X> type) {}
  public Command(String method, Map<String, Object> params, Function<Object, X> mapper) {}
}
JAVA

RUN cat > /workspace/stubs/org/openqa/selenium/bidi/Event.java <<'JAVA'
package org.openqa.selenium.bidi;

public class Event<X> {
  public String getMethod() { return ""; }
}
JAVA

RUN cat > /workspace/stubs/org/openqa/selenium/bidi/BiDiSessionStatus.java <<'JAVA'
package org.openqa.selenium.bidi;

public class BiDiSessionStatus {}
JAVA

# Reflective test class — lives in the image so test.sh can invoke it.
RUN mkdir -p /workspace/probe
RUN cat > /workspace/probe/BiDiProbe.java <<'JAVA'
import java.lang.annotation.Annotation;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.time.Duration;

public class BiDiProbe {
  public static void main(String[] args) throws Exception {
    String mode = args.length > 0 ? args[0] : "all";
    Class<?> bidiClass = Class.forName("org.openqa.selenium.bidi.BiDi");
    Class<?> connClass = Class.forName("org.openqa.selenium.bidi.Connection");

    if (mode.equals("ctor-exists") || mode.equals("all")) {
      Constructor<?> ctor = bidiClass.getConstructor(connClass);
      System.out.println("CTOR_EXISTS:OK:" + ctor.toString());
    }
    if (mode.equals("ctor-deprecated") || mode.equals("all")) {
      Constructor<?> ctor = bidiClass.getConstructor(connClass);
      Deprecated dep = ctor.getAnnotation(Deprecated.class);
      if (dep == null) {
        System.out.println("CTOR_DEPRECATED:FAIL:no @Deprecated annotation");
        System.exit(2);
      }
      System.out.println("CTOR_DEPRECATED:OK:forRemoval=" + dep.forRemoval());
    }
    if (mode.equals("default-timeout") || mode.equals("all")) {
      Constructor<?> ctor = bidiClass.getConstructor(connClass);
      Object connection = connClass.getDeclaredConstructor().newInstance();
      Object bidi = ctor.newInstance(connection);
      Field timeoutField = bidiClass.getDeclaredField("timeout");
      timeoutField.setAccessible(true);
      Duration timeout = (Duration) timeoutField.get(bidi);
      System.out.println("DEFAULT_TIMEOUT:OK:seconds=" + timeout.getSeconds());
    }
    if (mode.equals("two-arg-ctor") || mode.equals("all")) {
      Constructor<?> ctor = bidiClass.getConstructor(connClass, Duration.class);
      Object connection = connClass.getDeclaredConstructor().newInstance();
      Object bidi = ctor.newInstance(connection, Duration.ofSeconds(7));
      Field timeoutField = bidiClass.getDeclaredField("timeout");
      timeoutField.setAccessible(true);
      Duration timeout = (Duration) timeoutField.get(bidi);
      System.out.println("TWO_ARG_CTOR:OK:seconds=" + timeout.getSeconds());
    }
  }
}
JAVA

RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
