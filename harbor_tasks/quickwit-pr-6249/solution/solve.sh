#!/bin/bash
set -e

cd /workspace/quickwit-repo/quickwit

# Apply the fix: replace .unwrap_or_default() with .unwrap_or(IngesterStatus::Ready)
# in the ingester_status function
sed -i 's/\.unwrap_or_default()/.unwrap_or(IngesterStatus::Ready)/' quickwit-cluster/src/member.rs

# Verify the change was applied
grep -n "unwrap_or(IngesterStatus::Ready)" quickwit-cluster/src/member.rs

# Add the test to the file
cat >> quickwit-cluster/src/member.rs <<'EOF'

#[cfg(test)]
mod tests {
    use chitchat::NodeState;
    use quickwit_proto::ingest::ingester::IngesterStatus;

    use super::NodeStateExt;

    #[test]
    fn test_ingester_status_defaults_to_ready_when_key_absent() {
        let node_state = NodeState::for_test();
        assert_eq!(node_state.ingester_status(), IngesterStatus::Ready);
    }
}
EOF
