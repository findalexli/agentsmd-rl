#!/usr/bin/env bash
set -euo pipefail

cd /workspace/open-skills

# Idempotency guard
if grep -qF "\"Use the ip-lookup skill to query at least four public IP information providers " "skills/ip-lookup/SKILL.md" && grep -qF "HTML=\"<html><head><style>body{background:white;}img{animation:spin 2s infinite;}" "skills/song-website/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ip-lookup/SKILL.md b/skills/ip-lookup/SKILL.md
@@ -0,0 +1,81 @@
+---
+name: ip-lookup
+description: Check an IP address across multiple public geolocation and reputation sources and return a best-matched location summary.
+---
+
+# IP Lookup Skill
+
+Purpose
+- Query multiple public IP information providers and aggregate results to produce a concise, best-match location and metadata summary for an IP address.
+
+What it does
+- Queries at least four public sources (e.g. ipinfo.io, ip-api.com, ipstack, geoip-db, db-ip, ipgeolocation.io) or their free endpoints.
+- Normalises returned data (country, region, city, lat/lon, org/ASN) and computes a simple match score.
+- Returns a compact summary with the best-matched source and a short table of the other sources.
+
+Notes
+- Public APIs may have rate limits or require API keys for high volume; the skill falls back to free endpoints when possible.
+- Geolocation is approximate; ISP/gateway locations may differ from end-user locations.
+
+Bash example (uses curl + jq):
+
+```bash
+# Basic usage: IP passed as first arg
+IP=${1:-8.8.8.8}
+
+# Query 4 sources
+A=$(curl -s "https://ipinfo.io/${IP}/json")
+B=$(curl -s "http://ip-api.com/json/${IP}?fields=status,country,regionName,city,lat,lon,org,query")
+C=$(curl -s "https://geolocation-db.com/json/${IP}&position=true")
+D=$(curl -s "https://api.db-ip.com/v2/free/${IP}" )
+
+# Output best-match heuristics should be implemented in script
+echo "One-line summary:"
+jq -n '{ip:env.IP,sourceA:A,sourceB:B,sourceC:C,sourceD:D}' --argjson A "$A" --argjson B "$B" --argjson C "$C" --argjson D "$D"
+```
+
+Node.js example (recommended):
+
+```javascript
+// ip_lookup.js
+async function fetchJson(url, timeout = 8000){
+  const controller = new AbortController();
+  const id = setTimeout(()=>controller.abort(), timeout);
+  try { const res = await fetch(url, {signal: controller.signal}); clearTimeout(id); if(!res.ok) throw new Error(res.statusText); return await res.json(); } catch(e){ clearTimeout(id); throw e; }
+}
+
+async function ipLookup(ip){
+  const sources = {
+    ipinfo: `https://ipinfo.io/${ip}/json`,
+    ipapi: `http://ip-api.com/json/${ip}?fields=status,country,regionName,city,lat,lon,org,query`,
+    geodb: `https://geolocation-db.com/json/${ip}&position=true`,
+    dbip: `https://api.db-ip.com/v2/free/${ip}`
+  };
+
+  const results = {};
+  for(const [k,u] of Object.entries(sources)){
+    try{ results[k] = await fetchJson(u); } catch(e){ results[k] = {error: e.message}; }
+  }
+
+  // Normalise and pick best match (simple majority on country+city)
+  const votes = {};
+  for(const r of Object.values(results)){
+    if(!r || r.error) continue;
+    const country = r.country || r.country_name || r.countryCode || null;
+    const city = r.city || r.city_name || null;
+    const key = `${country||'?'}/${city||'?'}`;
+    votes[key] = (votes[key]||0)+1;
+  }
+  const best = Object.entries(votes).sort((a,b)=>b[1]-a[1])[0];
+  return {best: best?best[0]:null,score: best?best[1]:0,results};
+}
+
+// Usage: node ip_lookup.js 8.8.8.8
+```
+
+Agent prompt
+------------
+
+"Use the ip-lookup skill to query at least four public IP information providers for {ip}. Return a short JSON summary: best_match (country/city), score, and per-source details (country, region, city, lat, lon, org). Respect rate limits and fall back to alternate endpoints on errors."
+
+"When creating a new skill, follow SKILL_TEMPLATE.md format and include Node.js and Bash examples." 
diff --git a/skills/song-website/SKILL.md b/skills/song-website/SKILL.md
@@ -0,0 +1,111 @@
+---
+name: song-website
+description: Generate a minimal animated song website with album art, lyrics, and Wikipedia links, then upload to originless.
+---
+
+# Song Website Skill
+
+Purpose: Create a simple, animated HTML song card/website featuring album art, lyrics (user-provided or fetched legally), and related Wikipedia links, with a white background and lots of animations. Upload the generated index.html to originless for hosting.
+
+What it does:
+- Fetches song metadata (album art, artist info) from public APIs like iTunes or MusicBrainz.
+- Generates an HTML page with:
+  - White background.
+  - Animations (fade-ins, bounces, rotations on hover).
+  - Album art image.
+  - Lyrics section (user-provided; do not fetch copyrighted lyrics).
+  - Footer with Wikipedia links (artist, song, album).
+- Uploads the HTML to originless (https://originless.io or similar service) for free hosting.
+
+Files:
+- song_website_generator.js — Node.js script to generate and upload the HTML.
+
+Prerequisites:
+- Node.js 18+ (native fetch).
+- curl for Bash examples.
+- No API keys needed (uses free endpoints).
+
+Bash example (fetches album art via iTunes API, generates HTML, uploads to originless):
+
+```bash
+SONG="Armed and Dangerous"
+ARTIST="King Von"
+
+# Fetch album art URL
+ART_URL=$(curl -s "https://itunes.apple.com/search?term=${ARTIST} ${SONG}&limit=1" | jq -r '.results[0].artworkUrl100 // empty')
+
+# Generate HTML (simplified; add animations in full script)
+HTML="<html><head><style>body{background:white;}img{animation:spin 2s infinite;}@keyframes spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}</style></head><body><h1>${SONG}</h1><img src='${ART_URL}'><p>Lyrics here...</p><a href='https://en.wikipedia.org/wiki/King_Von'>Wikipedia</a></body></html>"
+
+# Upload to originless (use their API or manual upload; example uses curl to their endpoint)
+curl -X POST -H "Content-Type: text/html" --data-binary "$HTML" https://api.originless.io/upload
+```
+
+Node.js example (recommended; generates full animated HTML with lyrics placeholder, uploads to originless):
+
+```javascript
+async function generateSongWebsite(song, artist, lyrics = "Lyrics go here...") {
+  // Fetch album art
+  const search = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(artist + ' ' + song)}&limit=1`);
+  const data = await search.json();
+  const artUrl = data.results[0]?.artworkUrl100?.replace('100x100', '300x300') || 'https://via.placeholder.com/300';
+
+  // Generate HTML with animations
+  const html = `
+<!doctype html>
+<html lang="en">
+<head>
+  <meta charset="utf-8">
+  <title>${song} - ${artist}</title>
+  <style>
+    body { background: white; font-family: Arial, sans-serif; padding: 20px; }
+    .card { max-width: 600px; margin: 0 auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); animation: fadeIn 1s; }
+    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
+    img { width: 300px; height: 300px; border-radius: 10px; animation: bounce 3s infinite; }
+    @keyframes bounce { 0%, 20%, 50%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-10px); } 60% { transform: translateY(-5px); } }
+    h1 { animation: slideIn 1s; }
+    @keyframes slideIn { from { transform: translateX(-100%); } to { transform: translateX(0); } }
+    p { animation: fadeIn 2s; }
+    a { color: blue; animation: pulse 2s infinite; }
+    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
+  </style>
+</head>
+<body>
+  <div class="card">
+    <h1>${song} by ${artist}</h1>
+    <img src="${artUrl}" alt="Album Art">
+    <h2>Lyrics</h2>
+    <p>${lyrics.replace(/\n/g, '<br>')}</p>
+    <h2>Related Wikipedia</h2>
+    <a href="https://en.wikipedia.org/wiki/${encodeURIComponent(song)}">Song Page</a> |
+    <a href="https://en.wikipedia.org/wiki/${encodeURIComponent(artist)}">Artist Page</a> |
+    <a href="https://en.wikipedia.org/wiki/${encodeURIComponent(song)}_(song)">Album/Song Wiki</a>
+  </div>
+</body>
+</html>
+  `;
+
+  // Upload to originless (example endpoint; adjust for their API)
+  const uploadRes = await fetch('https://api.originless.io/upload', {
+    method: 'POST',
+    headers: { 'Content-Type': 'text/html' },
+    body: html
+  });
+  const uploadData = await uploadRes.json();
+  return { html, uploadUrl: uploadData.url };
+}
+
+// Usage
+// generateSongWebsite('Armed and Dangerous', 'King Von').then(console.log);
+```
+
+Notes:
+- Album art fetched from iTunes (free, no key).
+- Lyrics: User-provided; do not fetch copyrighted lyrics.
+- Animations: CSS keyframes for fade-in, bounce, slide, pulse.
+- Upload: Assumes originless.io API; check their docs for exact endpoint.
+- Legal: Only use for non-commercial, fair-use purposes.
+
+See also:
+- SKILL_TEMPLATE.md
+
PATCH

echo "Gold patch applied."
