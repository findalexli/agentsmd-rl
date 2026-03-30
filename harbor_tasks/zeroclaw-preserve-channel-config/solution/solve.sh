#!/usr/bin/env bash
set -euo pipefail
cd /workspace/zeroclaw

TARGET="src/onboard/wizard.rs"

# Change setup_channels() to accept Option<ChannelsConfig>
sed -i 's/fn setup_channels() -> Result<ChannelsConfig>/fn setup_channels(existing: Option<ChannelsConfig>) -> Result<ChannelsConfig>/' "$TARGET"

# Use existing config or default
sed -i 's/let mut config = ChannelsConfig::default();/let mut config = existing.unwrap_or_default();/' "$TARGET"

# Update call in run_wizard (fresh setup) to pass None
sed -i 's/let channels_config = setup_channels()?;/let channels_config = setup_channels(None)?;/' "$TARGET"

# Update call in run_channels_repair_wizard to pass existing config
sed -i 's/config\.channels_config = setup_channels()?;/config.channels_config = setup_channels(Some(config.channels_config.clone()))?;/' "$TARGET"
