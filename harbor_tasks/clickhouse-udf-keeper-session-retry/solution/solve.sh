#!/bin/bash
set -e

cd /workspace/clickhouse

FILE="src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"

# 1. Add includes after KeeperException.h
sed -i '/#include <Common\/ZooKeeper\/KeeperException.h>/a #include <Common/ZooKeeper/ZooKeeperCommon.h>\n#include <Common/ZooKeeper/ZooKeeperRetries.h>' "$FILE"

# 2. Add specific KeeperException catch block before the generic catch block in tryLoadObject
# Find the pattern and insert before it
sed -i '/^    catch (\.\.\.)/i\    catch (const zkutil::KeeperException \& e)\n    {\n        if (Coordination::isHardwareError(e.code))\n        {\n            LOG_WARNING(log, "Keeper hardware error while loading user defined SQL object {}: {}",\n                backQuote(object_name), e.message());\n            throw; /// Re-throw hardware errors so the caller can handle them properly\n        }\n        tryLogCurrentException(log, fmt::format("while loading user defined SQL object {}", backQuote(object_name)));\n        return nullptr; /// Non-hardware Keeper errors — treat as missing\n    }\n' "$FILE"

# 3. Modify refreshObjects function to use ZooKeeperRetriesControl
# First, add the comment and constants after "LOG_DEBUG(log, "Refreshing all user-defined {} objects", object_type);"
sed -i 's/LOG_DEBUG(log, "Refreshing all user-defined {} objects", object_type);/LOG_DEBUG(log, "Refreshing all user-defined {} objects", object_type);\n\n    \/\/\/ Read \& parse all SQL objects from ZooKeeper.\n    \/\/\/ Use ZooKeeperRetriesControl so that transient Keeper hiccups (brief connection\n    \/\/\/ blips, session jitter) are retried with backoff instead of aborting the entire\n    \/\/\/ refresh cycle and falling back to the 5-second sleep in processWatchQueue.\n    \/\/\/ tryLoadObject re-throws Keeper hardware errors, which ZooKeeperRetriesControl\n    \/\/\/ catches and retries automatically.  If retries are exhausted the exception\n    \/\/\/ propagates to the caller, so we never reach setAllObjects with a partial set.\n    static constexpr UInt64 max_retries = 5;\n    static constexpr UInt64 initial_backoff_ms = 200;\n    static constexpr UInt64 max_backoff_ms = 5000;/' "$FILE"

# Replace the simple loop with retryLoop version
# This is tricky with sed, let's use a different approach - rewrite the entire refreshObjects function

cat > /tmp/refresh_fix.py << 'PYTHON'
import re

with open("/workspace/clickhouse/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp", "r") as f:
    content = f.read()

# Find and replace the simple for loop in refreshObjects
old_pattern = r'''    /// Read & parse all SQL objects from ZooKeeper
    std::vector<std::pair<String, ASTPtr>> function_names_and_asts;
    for \(const auto & function_name : object_names\)
    \{
        if \(auto ast = tryLoadObject\(zookeeper, UserDefinedSQLObjectType::Function, function_name\)\)
            function_names_and_asts\.emplace_back\(function_name, ast\);
    \}'''

new_code = '''    /// Read & parse all SQL objects from ZooKeeper.
    /// Use ZooKeeperRetriesControl so that transient Keeper hiccups (brief connection
    /// blips, session jitter) are retried with backoff instead of aborting the entire
    /// refresh cycle and falling back to the 5-second sleep in processWatchQueue.
    /// tryLoadObject re-throws Keeper hardware errors, which ZooKeeperRetriesControl
    /// catches and retries automatically.  If retries are exhausted the exception
    /// propagates to the caller, so we never reach setAllObjects with a partial set.
    static constexpr UInt64 max_retries = 5;
    static constexpr UInt64 initial_backoff_ms = 200;
    static constexpr UInt64 max_backoff_ms = 5000;

    std::vector<std::pair<String, ASTPtr>> function_names_and_asts;

    ZooKeeperRetriesControl retries_ctl(
        "refreshObjects",
        log,
        ZooKeeperRetriesInfo{max_retries, initial_backoff_ms, max_backoff_ms, /*query_status=*/nullptr});

    retries_ctl.retryLoop([&]
    {
        function_names_and_asts.clear();
        for (const auto & function_name : object_names)
        {
            if (auto ast = tryLoadObject(zookeeper, UserDefinedSQLObjectType::Function, function_name))
                function_names_and_asts.emplace_back(function_name, ast);
        }
    });'''

# Try exact match first
if "/// Read & parse all SQL objects from ZooKeeper" in content:
    # Manual replacement
    old_section = '''    /// Read & parse all SQL objects from ZooKeeper
    std::vector<std::pair<String, ASTPtr>> function_names_and_asts;
    for (const auto & function_name : object_names)
    {
        if (auto ast = tryLoadObject(zookeeper, UserDefinedSQLObjectType::Function, function_name))
            function_names_and_asts.emplace_back(function_name, ast);
    }'''

    if old_section in content:
        content = content.replace(old_section, new_code)
        with open("/workspace/clickhouse/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp", "w") as f:
            f.write(content)
        print("Successfully updated refreshObjects")
    else:
        print("Could not find exact section match")
        exit(1)
else:
    print("Could not find section header")
    exit(1)
PYTHON

python3 /tmp/refresh_fix.py

# Verify idempotent application
echo "Verifying patch application..."
grep -q "ZooKeeperRetriesControl" "$FILE" || {
    echo "ERROR: Patch was not applied successfully - ZooKeeperRetriesControl not found"
    exit 1
}

grep -q "isHardwareError" "$FILE" || {
    echo "ERROR: Patch was not applied successfully - isHardwareError not found"
    exit 1
}

grep -q "ZooKeeperCommon.h" "$FILE" || {
    echo "ERROR: Patch was not applied successfully - ZooKeeperCommon.h include not found"
    exit 1
}

grep -q "ZooKeeperRetries.h" "$FILE" || {
    echo "ERROR: Patch was not applied successfully - ZooKeeperRetries.h include not found"
    exit 1
}

grep -q "retries_ctl.retryLoop" "$FILE" || {
    echo "ERROR: Patch was not applied successfully - retryLoop not found"
    exit 1
}

echo "Patch applied successfully"
