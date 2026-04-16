#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the fix for use-after-scope in parallel Object type deserialization
# Using sed to insert the SCOPE_EXIT block after the task_size line

sed -i '/size_t task_size = std::max(structure_state_concrete->sorted_dynamic_paths->size() \/ num_tasks, 1ul);/a\
\
        /// Ensure all already-scheduled tasks are drained on any exit path (including exceptions),\
        /// so pool threads do not dereference dangling references to stack locals.\
        SCOPE_EXIT(\
            for (const auto \& task : tasks)\
                task->tryExecute();\
            for (const auto \& task : tasks)\
                task->wait();\
        );\
' src/DataTypes/Serializations/SerializationObject.cpp

# Verify the patch was applied
grep -q "SCOPE_EXIT" src/DataTypes/Serializations/SerializationObject.cpp && echo "Patch applied successfully"
