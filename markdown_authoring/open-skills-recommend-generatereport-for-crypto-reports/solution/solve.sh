#!/usr/bin/env bash
set -euo pipefail

cd /workspace/open-skills

# Idempotency guard
if grep -qF "> Calculate both the straight-line (Haversine) distance and the driving distance" "skills/city-distance/SKILL.md" && grep -qF "Agent note: When producing human-friendly reports, agents should use the `skills" "skills/get-crypto-price/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/city-distance/SKILL.md b/skills/city-distance/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: city-distance
+description: Calculate line-of-sight and road distances between two cities using free OpenStreetMap services.
+---
+
 # City Distance Skill
 
 Purpose: Calculate line-of-sight and road distances between two cities using free, API-keyless public services and local haversine calculations.
@@ -9,12 +14,79 @@ What it does:
 
 Files:
 - city_distance_calculator.js — example Node.js script demonstrating the calculations.
+- examples: EXAMPLES.md with worked examples (Paris–Berlin, Paris–Dubai)
+
+When to use:
+- Quickly get straight-line and driving distances between two cities without paying for an API.
+- Generate a rough list of settlements along a driving route for planning or visualization.
+
+Prerequisites:
+- Node.js 18+ for the Node.js examples (native fetch available)
+- curl and jq for Bash examples
+
+Agent prompt:
+> Calculate both the straight-line (Haversine) distance and the driving distance between {cityA} and {cityB} using free OpenStreetMap services. Return distances in km and optionally list major towns along the driving route.
+
+Examples
+--------
+
+Bash (uses OSM routing, jq):
+
+```bash
+set -euo pipefail
+CITY_A_LAT=48.8566
+CITY_A_LON=2.3522
+CITY_B_LAT=52.52
+CITY_B_LON=13.4050
 
-Usage:
-1. Run `node city_distance_calculator.js` with Node.js 18+ (or install node-fetch for older Node versions).
-2. The script prints line-of-sight and road distances.
+URL="https://routing.openstreetmap.de/routed-car/route/v1/driving/${CITY_A_LON},${CITY_A_LAT};${CITY_B_LON},${CITY_B_LAT}?overview=false"
+
+curl -fsS --max-time 10 "$URL" | jq -r '.routes[0].distance / 1000'
+```
+
+Node.js (uses native fetch, AbortController, error handling):
+
+```javascript
+// city_distance_calculator.js
+async function fetchJson(url, timeoutMs = 10000) {
+  const controller = new AbortController();
+  const id = setTimeout(() => controller.abort(), timeoutMs);
+  try {
+    const res = await fetch(url, { signal: controller.signal });
+    clearTimeout(id);
+    if (!res.ok) throw new Error(`HTTP ${res.status}`);
+    return await res.json();
+  } catch (err) {
+    clearTimeout(id);
+    throw err;
+  }
+}
+
+function haversine(lat1, lon1, lat2, lon2) {
+  const R = 6371e3;
+  const toRad = d => (d * Math.PI) / 180;
+  const φ1 = toRad(lat1), φ2 = toRad(lat2);
+  const Δφ = toRad(lat2 - lat1), Δλ = toRad(lon2 - lon1);
+  const a = Math.sin(Δφ/2)**2 + Math.cos(φ1)*Math.cos(φ2)*Math.sin(Δλ/2)**2;
+  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
+  return (R * c) / 1000;
+}
+
+(async () => {
+  const paris = { lat: 48.8566, lon: 2.3522 };
+  const berlin = { lat: 52.52, lon: 13.4050 };
+  console.log('Line-of-sight (km):', haversine(paris.lat, paris.lon, berlin.lat, berlin.lon).toFixed(2));
+
+  const url = `https://routing.openstreetmap.de/routed-car/route/v1/driving/${paris.lon},${paris.lat};${berlin.lon},${berlin.lat}?overview=false`;
+  const data = await fetchJson(url, 15000);
+  console.log('Driving distance (km):', (data.routes[0].distance / 1000).toFixed(2));
+})();
+```
 
 Notes / Rate limits:
 - routing.openstreetmap.de and Nominatim are public services and have usage policies and rate limits. Use respectfully (cache results, avoid heavy automated polling).
 - For production-grade use, consider hosting your own OSRM/GraphHopper instance or using a commercial API with SLA.
 
+See also:
+- SKILL_TEMPLATE.md
+
diff --git a/skills/get-crypto-price/SKILL.md b/skills/get-crypto-price/SKILL.md
@@ -197,3 +197,9 @@ const atl = Math.min(...window.map(c => c[3]));
 ---
 
 If you want, I can add ready-to-run scripts for specific coins (BTC, ETH) and automate paginated Binance fetches to guarantee 90 days of hourly data.
+
+
+Agent note: When producing human-friendly reports, agents should use the `skills/generate-report` skill to produce formatted outputs (markdown or PDF). See `skills/generate-report/SKILL.md` for examples and templates.
+
+Example agent prompt:
+> Use the generate-report skill to create a short Bitcoin price report (current price, 24h change, 7d change) in markdown and PDF. Include source URLs.
PATCH

echo "Gold patch applied."
