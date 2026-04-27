#!/usr/bin/env bash
set -euo pipefail

cd /workspace/narrator-ai-cli-skill

# Idempotency guard
if grep -qF "description: \"CLI client for Narrator AI video narration API. Create AI-narrated" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: narrator-ai-cli
-description: "CLI client for Narrator AI video narration API. Create AI-narrated videos: popular-learning, generate-writing, clip-data, video-composing, magic-video. Supports Hot Drama / Original Mix / New Drama modes. 93 pre-built movies, 146 BGM tracks, 63 dubbing voices, 90+ narration templates. Use when user needs to create AI narration videos, manage narration tasks, browse dubbing/BGM/material resources, or automate video production via narrator-ai-cli."
+description: "CLI client for Narrator AI video narration API. Create AI-narrated videos: popular-learning, generate-writing, clip-data, video-composing, magic-video. Supports Hot Drama / Original Mix / New Drama modes. 93 pre-built movies, 146 BGM tracks, 63 dubbing voices, 90+ narration templates. Supports uploading local files or transferring from HTTP/Baidu/PikPak links. Use when user needs to create AI narration videos, manage narration tasks, browse dubbing/BGM/material resources, or automate video production via narrator-ai-cli."
 user-invocable: true
 metadata:
   {
@@ -140,6 +140,11 @@ narrator-ai-cli material genres --json
 narrator-ai-cli file upload ./movie.mp4 --json    # Returns file_id
 narrator-ai-cli file upload ./subtitles.srt --json
 narrator-ai-cli file list --json
+narrator-ai-cli file transfer --link "<url>" --json          # transfer by HTTP/Baidu/PikPak link
+narrator-ai-cli file info <file_id> --json
+narrator-ai-cli file download <file_id> --json
+narrator-ai-cli file storage --json
+narrator-ai-cli file delete <file_id> --json
 ```
 
 Supported formats: .mp4, .mkv, .mov, .mp3, .m4a, .wav, .srt, .jpg, .jpeg, .png
PATCH

echo "Gold patch applied."
