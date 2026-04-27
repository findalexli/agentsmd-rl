# Add new cache origins to the registry router

The Tuist registry router is a Cloudflare Worker that geo-routes requests for
`registry.tuist.dev` to the nearest healthy cache origin. Its routing table
lives in `infra/registry-router/src/index.ts` as the module-private constant
`ORIGINS: Origin[]`. Each entry is `{ host: string, lat: number, lon: number }`
and the `sortedByDistance(lat, lon)` helper ranks origins by haversine
distance from a request's lat/lon, with the first element being the chosen
origin.

The current routing table is missing coverage. Two gaps to close:

## 1. Australian users have no nearby origin

A request from Sydney (lat `-33.87`, lon `151.21`) is currently routed to
the Singapore origin (`cache-ap-southeast.tuist.dev`, lat `1.35`, lon
`103.82`) — roughly 6,300 km away — because there is no origin south of the
equator on the Pacific rim.

Register a new origin **`cache-au-east.tuist.dev`** in eastern Australia
(Sydney) so that Australian and Oceanian traffic routes there instead.
After the change, `sortedByDistance` called from Sydney coordinates must
return `cache-au-east.tuist.dev` as the first element. Melbourne and
Brisbane should also prefer the same origin.

## 2. Add capacity in Ashburn

The us-east region is being expanded from one node to three. Register two
additional origins, **`cache-us-east-2.tuist.dev`** and
**`cache-us-east-3.tuist.dev`**, both colocated with the existing
`cache-us-east.tuist.dev` (Ashburn, VA — lat `39.04`, lon `-77.49`). They
should sit alongside `cache-us-east.tuist.dev` in `ORIGINS` so that, for a
request near Ashburn, the top three nearest origins are exactly the three
`cache-us-east*.tuist.dev` hosts (in any order).

The pre-existing six origins (eu-central, eu-north, us-east, us-west,
ap-southeast, sa-west) must remain in the table with their current
coordinates; routing for known points (Frankfurt, Portland, Singapore,
Santiago) must still pick the same continental origin as before.

## Hostname and constant invariants

- The exact new hostnames are `cache-au-east.tuist.dev`,
  `cache-us-east-2.tuist.dev`, `cache-us-east-3.tuist.dev`.
- Each must appear exactly once in `ORIGINS`.
- The structure of an `Origin` (`{ host, lat, lon }`) and the existing
  `sortedByDistance` / `haversineDistance` helpers must keep working — do
  not rename or remove them.

## Repo conventions

- Per the root `AGENTS.md` "Intent Layer Maintenance" rule, when you change
  files in a directory that has its own `AGENTS.md`, keep that
  `AGENTS.md` in sync. The `infra/AGENTS.md` document includes a bullet
  list under **Origins:** that enumerates every cache host; it must
  continue to list every entry in `ORIGINS` after your change (i.e., add
  the three new hostnames as bullets there).
- Do not modify `CHANGELOG.md` (auto-generated).
- Edit only English-language content.

## Verifying locally

The `infra/registry-router/` package has no test runner; the package's CI
check is `tsc --noEmit` (a strict type-check using
`@cloudflare/workers-types`). Run it from `infra/registry-router/`:

```
npx tsc --noEmit
```

It must continue to succeed after your edits.
