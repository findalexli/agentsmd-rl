#!/bin/bash
set -e

cd /workspace/lancedb

# Check if already applied (look for fast_search in LanceFtsQueryBuilder specifically)
if grep -A 20 "class LanceFtsQueryBuilder" python/python/lancedb/query.py | grep -q "def fast_search"; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the Python query.py changes using sed
cd python/python/lancedb

# Add self._fast_search = None in __init__ after self._reranker = None
sed -i '/self._reranker = None/a\        self._fast_search = None' query.py

# Add fast_search method after phrase_query method
cat > /tmp/fast_search_method.txt << 'EOF'

    def fast_search(self) -> "LanceFtsQueryBuilder":
        """
        Skip a flat search of unindexed data. This will improve
        search performance but search results will not include unindexed data.

        Returns
        -------
        LanceFtsQueryBuilder
            The LanceFtsQueryBuilder object.
        """
        self._fast_search = True
        return self
EOF

# Find the line number where phrase_query method ends (the return self line)
LINE=$(grep -n "self._phrase_query = phrase_query" query.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    # Get the line with return self after phrase_query
    RET_LINE=$((LINE + 1))
    # Insert the new method after the return self line
    sed -i "${RET_LINE}r /tmp/fast_search_method.txt" query.py
fi

# Add fast_search to Query constructor call in LanceFtsQueryBuilder.to_query_object
# Find the specific context: offset=self._offset, followed by closing paren in that method
# We use a line number approach to be precise
# First find the line with "def to_query_object" in LanceFtsQueryBuilder section
FTS_CLASS_LINE=$(grep -n "class LanceFtsQueryBuilder" query.py | head -1 | cut -d: -f1)
if [ -n "$FTS_CLASS_LINE" ]; then
    # Find offset=self._offset, after the class definition but before the next class
    NEXT_CLASS_LINE=$(tail -n +$((FTS_CLASS_LINE + 1)) query.py | grep -n "^class " | head -1 | cut -d: -f1)
    if [ -n "$NEXT_CLASS_LINE" ]; then
        NEXT_CLASS_LINE=$((FTS_CLASS_LINE + NEXT_CLASS_LINE))
    else
        NEXT_CLASS_LINE=$(wc -l < query.py)
    fi
    # Find offset=self._offset, between FTS class and next class
    OFFSET_LINE=$(sed -n "${FTS_CLASS_LINE},${NEXT_CLASS_LINE}p" query.py | grep -n "offset=self._offset," | head -1 | cut -d: -f1)
    if [ -n "$OFFSET_LINE" ]; then
        ACTUAL_LINE=$((FTS_CLASS_LINE + OFFSET_LINE - 1))
        sed -i "${ACTUAL_LINE}a\            fast_search=self._fast_search," query.py
    fi
fi

echo "Patch applied successfully"
