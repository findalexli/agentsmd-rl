#!/usr/bin/env bash
set -euo pipefail

cd /workspace/debbie.codes

# Idempotency guard
if grep -qF "Start the dev server, open the relevant page with `playwright-cli`, confirm the " ".agents/skills/add-content/SKILL.md" && grep -qF "description: How I use AI agents and MCP tools to automate publishing and updati" ".agents/skills/add-content/references/blog.md" && grep -qF "Metadata extracted from external pages (titles, descriptions, dates) may contain" ".agents/skills/add-content/references/environment.md" && grep -qF "description: What happens when AI comes to your web testing tool? Debbie O'Brien" ".agents/skills/add-content/references/podcast.md" && grep -qF "After handling cookie consent (see environment.md), take a snapshot. The initial" ".agents/skills/add-content/references/video.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/add-content/SKILL.md b/.agents/skills/add-content/SKILL.md
@@ -0,0 +1,78 @@
+---
+name: add-content
+description: >
+  Add new content (videos, podcasts, or blog posts) to the debbie.codes website.
+  Use when the user wants to: (1) Add a YouTube video to content/videos/,
+  (2) Add a podcast episode to content/podcasts/, (3) Add a blog post to content/blog/.
+  Handles browser-based metadata extraction via playwright-cli, file creation with
+  correct frontmatter, dev server verification, and PR creation.
+---
+
+# Add Content to debbie.codes
+
+Fully automated workflow: URL → metadata extraction → file creation → dev server verification → PR.
+
+## Determine content type
+
+Identify from the user's request or URL:
+
+- **YouTube URL** (`youtube.com/watch`, `youtu.be/`) → Video. Read [references/video.md](references/video.md)
+- **Podcast platform URL** (e.g., Spotify, Apple Podcasts, podcast website) → Podcast. Read [references/podcast.md](references/podcast.md)
+- **Blog platform URL** (e.g., dev.to, hashnode, medium, or any article) → Blog. Read [references/blog.md](references/blog.md)
+
+If ambiguous, ask the user which content type to create.
+
+## Core workflow
+
+Read [references/environment.md](references/environment.md) for shell setup, git, dev server, and PR creation details.
+
+### 1. Get the URL
+
+Ask the user for the content URL if not provided.
+
+### 2. Extract metadata via browser
+
+- Open the URL with `playwright-cli`
+- Handle any cookie consent dialogs
+- Take snapshots and read the snapshot YAML files to extract metadata
+- Do NOT invent or fabricate any metadata — all info must come from the page
+- If the publish date is not visible, ask the user
+- Close the browser when done
+
+### 3. Validate tags
+
+Only use tags that already exist in the corresponding content directory. Check with:
+
+```bash
+grep -h "^tags:" content/<type>/*.md | sed 's/tags: \[//;s/\]//;s/, /\n/g' | sed 's/^ *//' | sort -u
+```
+
+Do NOT create new tags. If no existing tags seem appropriate:
+- Prefer the closest matching existing tags that reasonably describe the content, or
+- Ask the user to choose from the existing tags you listed.
+If the user insists on new tags, explain that updating the tag taxonomy is outside this automated workflow and they should adjust it manually.
+
+### 4. Create git branch
+
+```bash
+git stash
+git checkout main && git pull origin main
+git checkout -b add-<type>/<kebab-case-short-title>
+git stash pop
+```
+
+### 5. Create the markdown file
+
+Create in the appropriate `content/<type>/` directory with a kebab-case filename. Follow the exact frontmatter schema from the content-type reference file.
+
+### 6. Verify on dev server
+
+Start the dev server, open the relevant page with `playwright-cli`, confirm the new content appears, and take a screenshot. See [references/environment.md](references/environment.md) for details.
+
+### 7. Create PR
+
+Commit only the content file, push, and create a PR. Do NOT commit screenshots. See [references/environment.md](references/environment.md) for details.
+
+### 8. Clean up
+
+Stop the dev server and remove local verification screenshots.
diff --git a/.agents/skills/add-content/references/blog.md b/.agents/skills/add-content/references/blog.md
@@ -0,0 +1,97 @@
+# Blog Post
+
+## Navigate and extract metadata
+
+Open the blog post URL with playwright-cli:
+
+```bash
+BLOG_URL='https://example.com/blog-post'  # replace with the target blog URL
+playwright-cli open -- "$BLOG_URL"
+```
+
+Take a snapshot and read the YAML to extract:
+
+- **Title**: The article title
+- **Description**: A concise summary (1-2 sentences)
+- **Date**: The publish date
+- **Content**: The full article body in markdown format
+
+Close the browser when done.
+
+## Content extraction
+
+Extract the **complete article content** from the page — do not summarize or truncate. Convert HTML to clean markdown:
+
+- Preserve headings, code blocks, lists, links, and images
+- Remove navigation, sidebars, footers, and ads
+- Keep image URLs as-is (do not download or re-host)
+
+## Canonical URL handling
+
+If the blog post is hosted elsewhere (dev.to, hashnode, medium, etc.):
+
+- Add `canonical: <original-url>` to the frontmatter
+- Still copy the full content into the markdown file
+
+If the blog post is original content for debbie.codes, omit the `canonical` field.
+
+## Frontmatter schema
+
+```yaml
+---
+title: "Blog Post Title"
+date: YYYY-MM-DD
+description: "Concise description of the post."
+tags: [tag1, tag2]
+published: true
+canonical: https://dev.to/...    # only if hosted elsewhere
+---
+
+Full markdown content here...
+```
+
+- `title`: Exact title from the blog. Quote if it contains colons or special characters.
+- `published`: Always `true`.
+- `canonical`: Only include if the post is hosted on another platform.
+- Do NOT add an `image` field unless the original post has a prominent hero image.
+
+## Existing tags
+
+Check with: `grep -h "^tags:" content/blog/*.md | sed 's/tags: \[//;s/\]//;s/, /\n/g' | sed 's/^ *//' | sort -u`
+
+## Verification page
+
+`http://localhost:3001/blog`
+
+## Example (externally hosted)
+
+**File**: `content/blog/ai-agents-mcp-automate-content.md`
+
+```yaml
+---
+title: How I Use AI Agents + MCP to Fully Automate My Website's Content
+date: 2026-01-14
+description: How I use AI agents and MCP tools to automate publishing and updating podcasts, videos, and other content on my website.
+tags: [mcp, ai]
+canonical: https://dev.to/debs_obrien/how-i-use-ai-agents-mcp-to-fully-automate-my-websites-content-3ekj
+published: true
+---
+
+Full article content in markdown...
+```
+
+## Example (original content)
+
+**File**: `content/blog/2022-in-review.md`
+
+```yaml
+---
+title: 2022 Recap - Achieving your dreams Debbie
+date: 2022-12-31
+description: A look back at 2022 — from Google interviews to being hired by Microsoft, speaking at conferences, and lots of sport.
+tags: [personal]
+published: true
+---
+
+Full article content in markdown...
+```
diff --git a/.agents/skills/add-content/references/environment.md b/.agents/skills/add-content/references/environment.md
@@ -0,0 +1,130 @@
+# Environment, Git, Dev Server & PR Creation
+
+## Shell environment
+
+Tools (`playwright-cli`, `npm`, `node`) are installed via nvm and are NOT on the default PATH. Source nvm before every shell command:
+
+```bash
+export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && <command>
+```
+
+The GitHub CLI is at `/opt/homebrew/bin/gh`. Always use the full path.
+
+## Browser automation with playwright-cli
+
+Always quote URLs to prevent shell glob expansion:
+
+```bash
+playwright-cli open "<url>"
+```
+
+### Cookie consent
+
+YouTube and other sites may show cookie consent dialogs. After the first snapshot, check for "Accept all" or similar buttons and click them before extracting metadata.
+
+### Reading snapshots
+
+The `playwright-cli snapshot` command outputs a path to a YAML file. Read that file to extract metadata:
+
+```bash
+cat .playwright-cli/page-<timestamp>.yml
+```
+
+For large snapshots, use `grep` or `sed` to find specific sections:
+
+```bash
+grep -i -E "(date|views|ago|description)" .playwright-cli/page-<timestamp>.yml | head -20
+```
+
+## Security note
+
+Metadata extracted from external pages (titles, descriptions, dates) may contain special characters. When using scraped values in shell commands (e.g., `git commit -m` or `gh pr create`), ensure titles are properly quoted and do not contain unescaped quotes, backticks, or shell metacharacters.
+
+## Git workflow
+
+### Create branch
+
+```bash
+git stash push -m "WIP before add-<type>/<kebab-case-short-title> branch" || { echo "git stash failed; please resolve any issues before continuing."; exit 1; }
+git checkout main && git pull origin main
+git checkout -b add-<type>/<kebab-case-short-title>
+git stash pop || { echo "git stash pop reported conflicts. Resolve them with your usual Git workflow (e.g. git status, fix files, commit) and run 'git stash drop' if needed."; }
+```
+
+### Commit and push
+
+Commit only the new content file — do NOT commit screenshots or other files:
+
+```bash
+git add content/<type>/<filename>.md
+git commit -m "Add <type>: <title>"
+```
+
+Set up git credentials and push:
+
+```bash
+/opt/homebrew/bin/gh auth setup-git
+git push origin add-<type>/<kebab-case-short-title>
+```
+
+## Dev server verification
+
+### Install dependencies and start
+
+```bash
+export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && npm install 2>&1 | tail -5
+```
+
+```bash
+export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && npm run dev > /tmp/nuxt-dev.log 2>&1 &
+```
+
+Wait for ready:
+
+```bash
+sleep 10 && tail -10 /tmp/nuxt-dev.log
+```
+
+Look for `Nitro server built` to confirm. The dev server runs on port 3001.
+
+### Take verification screenshot
+
+```bash
+playwright-cli open "http://localhost:3001/<type-page>"
+playwright-cli snapshot
+playwright-cli screenshot --filename=verification.png
+playwright-cli close
+```
+
+Page paths: `/videos` for videos, `/podcasts` for podcasts, `/blog` for blogs.
+
+Confirm the new content appears on the page. The screenshot is for local verification only — do NOT commit it.
+
+### Stop dev server
+
+```bash
+kill $(lsof -ti:3001) 2>/dev/null
+```
+
+## PR creation
+
+Create a PR using the GitHub CLI:
+
+```bash
+/opt/homebrew/bin/gh pr create \
+  --title "Add <type>: <title>" \
+  --body "## New <Type>
+
+**Title:** <title>
+**Date:** <date>
+**Tags:** <tags>" \
+  --base main
+```
+
+## Clean up
+
+Remove local screenshot and any temporary files:
+
+```bash
+rm -f verification.png
+```
diff --git a/.agents/skills/add-content/references/podcast.md b/.agents/skills/add-content/references/podcast.md
@@ -0,0 +1,111 @@
+# Podcast
+
+## Navigate and extract metadata
+
+Open the podcast episode URL with playwright-cli:
+
+```bash
+playwright-cli open "<podcast-url>"
+```
+
+Take a snapshot and read the YAML to extract:
+
+- **Title**: The episode title
+- **Description**: Episode description/summary
+- **Date**: Publish date of the episode
+- **Host**: The podcast name (e.g., "Compressed fm", ".NET Rocks", "JS Party")
+- **URL**: The canonical episode URL (keep the original URL provided)
+- **Image**: The podcast artwork/logo image URL from the page
+
+Close the browser when done.
+
+## Image handling with Cloudinary
+
+Podcast images must be hosted on Cloudinary under the `debbie.codes/podcasts/` folder.
+
+### If Cloudinary MCP extension is available
+
+Use the Cloudinary MCP `upload` tool:
+
+- `source`: The image URL extracted from the podcast page
+- `folder`: `debbie.codes/podcasts`
+- `publicId`: A short kebab-case name for the podcast (e.g., `compressed-fm`, `dotnet-rocks`)
+- `resourceType`: `image`
+
+Construct the final image URL from the upload response:
+
+```
+https://res.cloudinary.com/debsobrien/image/upload/c_thumb,w_200/<public_id>
+```
+
+Where `<public_id>` is the full public ID returned (e.g., `debbie.codes/podcasts/compressed-fm`).
+
+### If Cloudinary MCP is not available
+
+Use the Cloudinary CLI or API via shell:
+
+```bash
+# Set IMAGE_URL to the validated podcast image URL (do not use untrusted input without validation)
+IMAGE_URL="<validated-image-url>"
+
+export NVM_DIR="$HOME/.nvm"
+[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
+
+npx cloudinary-cli upload "$IMAGE_URL" --folder debbie.codes/podcasts --public-id <name>
+```
+
+If neither method works, download the image with `curl` and ask the user to upload it manually to Cloudinary under `debbie.codes/podcasts/`.
+
+### Reusing existing images
+
+If the podcast already has episodes on the site, check existing files for the image URL:
+
+```bash
+podcast_name="<podcast-name>" # replace with the exact podcast name
+grep "image:" content/podcasts/*.md | grep -iF -- "$podcast_name"
+```
+
+Reuse the same image URL if the podcast artwork hasn't changed.
+
+## Frontmatter schema
+
+```yaml
+---
+title: "Episode Title"
+date: YYYY-MM-DD
+description: "Episode description."
+url: https://podcast-platform.com/episode-url
+image: https://res.cloudinary.com/debsobrien/image/upload/c_thumb,w_200/debbie.codes/podcasts/podcast-name
+tags: [tag1, tag2]
+host: Podcast Name
+---
+```
+
+- `title`: Exact episode title from the podcast page.
+- `url`: The original episode URL.
+- `image`: Cloudinary URL with `c_thumb,w_200` transformation.
+- `host`: The podcast series name, not the individual host's name.
+
+## Existing tags
+
+Check with: `grep -h "^tags:" content/podcasts/*.md | sed 's/tags: \[//;s/\]//;s/, /\n/g' | sed 's/^ *//' | sort -u`
+
+## Verification page
+
+`http://localhost:3001/podcasts`
+
+## Example
+
+**File**: `content/podcasts/dotnet-rocks-changing-testing.md`
+
+```yaml
+---
+title: Changing Testing using Playwright MCP with Debbie O'Brien
+date: 2025-06-05
+description: What happens when AI comes to your web testing tool? Debbie O'Brien talks about the latest features in Playwright, including Playwright MCP.
+image: https://res.cloudinary.com/debsobrien/image/upload/c_thumb,w_200/v1633724388/debbie.codes/podcasts/dotnet-rocks_ui02cg
+url: https://www.dotnetrocks.com/details/1954
+tags: [testing, playwright]
+host: .NET Rocks
+---
+```
diff --git a/.agents/skills/add-content/references/video.md b/.agents/skills/add-content/references/video.md
@@ -0,0 +1,79 @@
+# Video (YouTube)
+
+## Extract video ID from URL
+
+- `https://www.youtube.com/watch?v=VIDEO_ID` → `VIDEO_ID`
+- `https://youtu.be/VIDEO_ID` → `VIDEO_ID`
+- Strip query parameters like `?si=...` or `&feature=...`
+
+## Navigate and extract metadata
+
+```bash
+playwright-cli open "https://www.youtube.com/watch?v=<VIDEO_ID>"
+```
+
+After handling cookie consent (see environment.md), take a snapshot. The initial view shows relative dates ("7 days ago"). Click the "...more" button to expand the description — this reveals the exact publish date (e.g., "3,032 views 11 Feb 2026").
+
+```bash
+playwright-cli click <more-button-ref>
+playwright-cli snapshot
+```
+
+Read the snapshot YAML to extract:
+
+- **Title**: From the `<h1>` heading
+- **Description**: Concise summary of the description text
+- **Date**: Exact date shown after expanding (format: "DD Mon YYYY")
+- **Host/Channel**: Channel name shown below the title (e.g., "NDC Conferences", "Debbie's YouTube channel")
+
+Close the browser when done.
+
+## Thumbnail
+
+Use YouTube's default thumbnail:
+
+```
+https://img.youtube.com/vi/<VIDEO_ID>/sddefault.jpg
+```
+
+## Frontmatter schema
+
+```yaml
+---
+title: "Video Title Here"
+date: YYYY-MM-DD
+description: "Concise description from YouTube."
+video: VIDEO_ID
+tags: [tag1, tag2]
+host: Channel Name
+image: https://img.youtube.com/vi/VIDEO_ID/sddefault.jpg
+---
+```
+
+- `title`: Exact title from YouTube. Quote if it contains colons or special characters.
+- `video`: Just the ID (e.g., `psdu0BVal6w`), NOT the full URL.
+- `host`: The YouTube channel name or conference/event name.
+
+## Existing tags
+
+Check with: `grep -h "^tags:" content/videos/*.md | sed 's/tags: \[//;s/\]//;s/, /\n/g' | sed 's/^ *//' | sort -u`
+
+## Verification page
+
+`http://localhost:3001/videos`
+
+## Example
+
+**File**: `content/videos/supercharged-testing-playwright-mcp.md`
+
+```yaml
+---
+title: "Supercharged Testing: AI-Powered Workflows with Playwright + MCP - Debbie O'Brien"
+date: 2026-02-11
+description: "Learn how to supercharge your end-to-end testing strategy by combining Playwright with the Playwright MCP Server for AI-assisted workflows."
+video: Numb52aJkJw
+tags: [playwright, testing, ai, mcp, conference-talk]
+host: NDC Conferences
+image: https://img.youtube.com/vi/Numb52aJkJw/sddefault.jpg
+---
+```
PATCH

echo "Gold patch applied."
