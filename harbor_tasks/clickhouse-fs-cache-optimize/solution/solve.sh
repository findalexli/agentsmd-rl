#!/bin/bash
set -e

cd /workspace/clickhouse

# Fetch the PR diff from GitHub
curl -sL https://github.com/ClickHouse/ClickHouse/pull/101949.diff -o /tmp/pr.diff

echo "Attempting to apply PR diff..."

# Try to apply the diff - if it fails, use manual approach
if git apply --check /tmp/pr.diff 2>/dev/null; then
    echo "Diff can be applied cleanly, applying..."
    git apply /tmp/pr.diff
else
    echo "Standard apply would fail, trying with ignore-whitespace..."
    if git apply --ignore-whitespace --check /tmp/pr.diff 2>/dev/null; then
        echo "Applying with ignore-whitespace..."
        git apply --ignore-whitespace /tmp/pr.diff
    else
        echo "Diff cannot be applied cleanly. Using manual approach..."

        # Apply header file changes using sed
        sed -i 's/bool best_effort = false/bool is_initial_load = false/g' src/Interpreters/Cache/IFileCachePriority.h
        sed -i 's/bool best_effort = false/bool is_initial_load = false/g' src/Interpreters/Cache/LRUFileCachePriority.h
        sed -i 's/bool best_effort = false/bool is_initial_load = false/g' src/Interpreters/Cache/SLRUFileCachePriority.h
        sed -i 's/bool best_effort = false/bool is_initial_load = false/g' src/Interpreters/Cache/SplitFileCachePriority.h
        sed -i 's/bool is_startup = false/bool is_initial_load = false/g' src/Interpreters/Cache/SLRUFileCachePriority.h

        # Apply .cpp file changes
        sed -i 's/bool best_effort) const/bool is_initial_load) const/g' src/Interpreters/Cache/SLRUFileCachePriority.cpp
        sed -i 's/if (best_effort)/if (is_initial_load)/g' src/Interpreters/Cache/SLRUFileCachePriority.cpp
        sed -i 's/bool is_startup)/bool is_initial_load)/g' src/Interpreters/Cache/SLRUFileCachePriority.cpp
        sed -i 's/if (is_startup)/if (is_initial_load)/g' src/Interpreters/Cache/SLRUFileCachePriority.cpp

        sed -i 's/bool best_effort)/bool is_initial_load)/g' src/Interpreters/Cache/SplitFileCachePriority.cpp
        sed -i 's/state_lock, best_effort);/state_lock, is_initial_load);/g' src/Interpreters/Cache/SplitFileCachePriority.cpp
        sed -i 's/bool best_effort) const/bool is_initial_load) const/g' src/Interpreters/Cache/SplitFileCachePriority.cpp
        sed -i 's/origin_info, best_effort);/origin_info, is_initial_load);/g' src/Interpreters/Cache/SplitFileCachePriority.cpp

        # Apply FileCache.cpp changes using Python
        python3 << 'PYEOF'
import re

with open('src/Interpreters/Cache/FileCache.cpp', 'r') as f:
    lines = f.readlines()

output = []
i = 0
while i < len(lines):
    line = lines[i]

    # Add main_priority->check() after first_exception handling
    if 'std::rethrow_exception(first_exception);' in line and i + 2 < len(lines):
        output.append(line)
        i += 1
        if lines[i].strip() == '' and 'assertCacheCorrectness()' in lines[i+1]:
            output.append(lines[i])
            output.append('    main_priority->check(cache_state_guard.lock());\n')
            output.append('\n')
            i += 1
        continue

    # Remove function-level offset/size declarations
    if 'UInt64 offset = 0;' in line and i + 1 < len(lines) and 'UInt64 size = 0;' in lines[i+1]:
        i += 2
        continue

    # Add SegmentToLoad struct after key_metadata creation
    if '/* is_initial_load */true);' in line:
        output.append(line)
        i += 1
        # Check if next non-blank line starts the for loop
        while i < len(lines) and lines[i].strip() == '':
            output.append(lines[i])
            i += 1
        if i < len(lines) and 'for (fs::directory_iterator offset_it' in lines[i]:
            output.append('\n')
            output.append('        /// Phase 1: scan and parse all segment files for this key (no lock held).\n')
            output.append('        struct SegmentToLoad\n')
            output.append('        {\n')
            output.append('            UInt64 offset;\n')
            output.append('            UInt64 size;\n')
            output.append('            FileSegmentKind kind;\n')
            output.append('            fs::path path;\n')
            output.append('            IFileCachePriority::IteratorPtr cache_it; /// filled in phase 2\n')
            output.append('        };\n')
            output.append('        std::vector<SegmentToLoad> segments;\n')
        continue

    # Modify offset loop processing
    if 'FileSegmentKind segment_kind = FileSegmentKind::Regular;' in line:
        i += 1  # Skip this line entirely
        continue

    # Add opening brace to single-line if
    if 'if (delim_pos == std::string::npos)' in line and i + 1 < len(lines):
        next_line = lines[i+1]
        if 'parsed = tryParse' in next_line and '{' not in next_line:
            output.append('            if (delim_pos == std::string::npos)\n')
            output.append('            {\n')
            output.append(next_line)
            i += 2
            continue

    # Close the if brace before else
    if 'parsed = tryParse<UInt64>(offset, offset_with_suffix);' in line and i + 1 < len(lines):
        output.append(line)
        if 'else' in lines[i+1]:
            output.append('            }\n')
        i += 1
        continue

    # Fix spacing around delim_pos+1
    if 'delim_pos+1' in line:
        line = line.replace('delim_pos+1', 'delim_pos + 1')

    # Remove comment from continue line
    if 'continue; /// Or just remove? Some unexpected file.' in line:
        output.append('                continue;\n')
        i += 1
        continue

    # Change size declaration and trigger Phase 2/3 insertion
    if 'size = offset_it->file_size();' in line and i + 1 < len(lines):
        output.append('            auto size = offset_it->file_size();\n')
        i += 1

        # Now we need to find the end of the offset_it loop and add Phase 2/3
        # First, skip until we see bool limits_satisfied (the old block starts)
        while i < len(lines) and 'bool limits_satisfied;' not in lines[i]:
            if 'fs::remove(offset_it->path());' in lines[i] and 'continue;' in lines[i+1]:
                # This is a continue inside the offset_it loop - we need to add push_back
                output.append(lines[i])  # fs::remove
                output.append(lines[i+1])  # continue;
                output.append('            }\n')  # close the if block
                output.append('\n')
                output.append('            segments.push_back({offset, size, FileSegmentKind::Regular, offset_it->path(), nullptr});\n')
                i += 3

                # Now add Phase 2 and 3
                output.append('''        }

        /// Phase 2: add all segments for the key under a single write lock acquisition.
        /// TODO: we can get rid of this lockCache() if we first load everything in parallel
        /// without any mutual lock between loading threads, and only after do removeOverflow().
        /// This will be better because overflow here may
        /// happen only if cache configuration changed and max_size became less than it was.
        size_t size_limit = 0;
        {
            auto lock = cache_guard.writeLock();
            auto state_lock = cache_state_guard.lock();
            size_limit = main_priority->getSizeLimit(state_lock);

            for (auto & segment : segments)
            {
                if (main_priority->canFit(
                        segment.size,
                        /* elements */1,
                        state_lock,
                        /* reservee */nullptr,
                        origin_info,
                        /* is_initial_load */true))
                {
                    segment.cache_it = main_priority->add(
                        key_metadata,
                        segment.offset,
                        segment.size,
                        lock,
                        &state_lock,
                        /* is_initial_load */true);
                }
            }
        }

        /// Phase 3: construct FileSegment objects and emplace
        /// (no lock held, because a single key is loaded by a single thread).
        size_t failed_to_fit = 0;
        for (auto & segment : segments)
        {
            if (segment.cache_it)
            {
                bool inserted = false;
                try
                {
                    auto file_segment = std::make_shared<FileSegment>(
                        key,
                        segment.offset,
                        segment.size,
                        FileSegment::State::DOWNLOADED,
                        CreateFileSegmentSettings(segment.kind),
                        /* background_download_enabled */false,
                        this,
                        key_metadata,
                        segment.cache_it);

                    inserted = key_metadata->emplaceUnlocked(segment.offset, std::make_shared<FileSegmentMetadata>(std::move(file_segment))).second;
                }
                catch (...)
                {
                    tryLogCurrentException(__PRETTY_FUNCTION__);
                    chassert(false);
                }

                if (inserted)
                {
                    LOG_TEST(log, "Added file segment {}:{} (size: {}) with path: {}", key, segment.offset, segment.size, segment.path.string());
                }
                else
                {
                    segment.cache_it->remove(cache_guard.writeLock());
                    fs::remove(segment.path);
                    chassert(false);
                }
            }
            else
            {
                ++failed_to_fit;
                fs::remove(segment.path);
            }
        }

        if (failed_to_fit)
        {
            LOG_WARNING(
                log,
                "Cache capacity changed (max size: {}), "
                "{} file(s) for key {} do not fit in cache anymore",
                size_limit, failed_to_fit, key);
        }
''')
                # Now skip the rest of the old block (from bool limits_satisfied to end of offset_it loop)
                brace_depth = 1  # Inside the offset_it loop
                while i < len(lines) and brace_depth > 0:
                    brace_depth += lines[i].count('{') - lines[i].count('}')
                    i += 1
            else:
                output.append(lines[i])
                i += 1
        continue

    # Add offset declaration after parsed declaration
    if 'bool parsed;' in line and i + 1 < len(lines) and 'delim_pos' in lines[i+1]:
        output.append('            bool parsed;\n')
        output.append('            UInt64 offset = 0;\n')
        i += 1
        continue

    output.append(line)
    i += 1

with open('src/Interpreters/Cache/FileCache.cpp', 'w') as f:
    f.writelines(output)

print("Manual FileCache.cpp changes applied")
PYEOF
    fi
fi

# Verify the patch was applied
echo ""
echo "Verifying changes..."

errors=0

grep -q "main_priority->check(cache_state_guard.lock())" src/Interpreters/Cache/FileCache.cpp || { echo "ERROR: main_priority->check not found"; errors=$((errors+1)); }
grep -q "struct SegmentToLoad" src/Interpreters/Cache/FileCache.cpp || { echo "ERROR: SegmentToLoad not found"; errors=$((errors+1)); }
grep -q "is_initial_load = false" src/Interpreters/Cache/IFileCachePriority.h || { echo "ERROR: is_initial_load not found in IFileCachePriority.h"; errors=$((errors+1)); }
grep -q "Phase 1: scan and parse" src/Interpreters/Cache/FileCache.cpp || { echo "ERROR: Phase 1 comment not found"; errors=$((errors+1)); }
grep -q "Phase 2: add all segments" src/Interpreters/Cache/FileCache.cpp || { echo "ERROR: Phase 2 comment not found"; errors=$((errors+1)); }
grep -q "Phase 3: construct FileSegment" src/Interpreters/Cache/FileCache.cpp || { echo "ERROR: Phase 3 comment not found"; errors=$((errors+1)); }
grep -q "failed_to_fit = 0" src/Interpreters/Cache/FileCache.cpp || { echo "ERROR: failed_to_fit counter not found"; errors=$((errors+1)); }
grep -q "bool is_initial_load) const" src/Interpreters/Cache/SLRUFileCachePriority.cpp || { echo "ERROR: is_initial_load param not found in SLRUFileCachePriority.cpp"; errors=$((errors+1)); }

if [ $errors -eq 0 ]; then
    echo "All verifications passed!"
    exit 0
else
    echo ""
    echo "$errors verification(s) failed"
    exit 1
fi
