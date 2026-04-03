#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency check: if nextTestSetup is already imported, patch was applied
if grep -q 'nextTestSetup' test/e2e/edge-async-local-storage/index.test.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create fixture directory
mkdir -p test/e2e/edge-async-local-storage/pages/api

# Create single ALS fixture
cat > test/e2e/edge-async-local-storage/pages/api/single.js << 'FIXTURE'
export const config = { runtime: 'edge' }
// eslint-disable-next-line no-undef
const storage = new AsyncLocalStorage()

export default async function handler(request) {
  const id = request.headers.get('req-id')
  return storage.run({ id }, async () => {
    await getSomeData()
    return Response.json(storage.getStore())
  })
}

async function getSomeData() {
  try {
    const response = await fetch('https://example.vercel.sh')
    await response.text()
  } finally {
    return true
  }
}
FIXTURE

# Create multiple ALS fixture
cat > test/e2e/edge-async-local-storage/pages/api/multiple.js << 'FIXTURE'
export const config = { runtime: 'edge' }
// eslint-disable-next-line no-undef
const topStorage = new AsyncLocalStorage()

export default async function handler(request) {
  const id = request.headers.get('req-id')
  return topStorage.run({ id }, async () => {
    const nested = await getSomeData(id)
    return Response.json({ ...nested, ...topStorage.getStore() })
  })
}

async function getSomeData(id) {
  // eslint-disable-next-line no-undef
  const nestedStorage = new AsyncLocalStorage()
  return nestedStorage.run('nested-' + id, async () => {
    try {
      const response = await fetch('https://example.vercel.sh')
      await response.text()
    } finally {
      return { nestedId: nestedStorage.getStore() }
    }
  })
}
FIXTURE

# Rewrite the test file to use nextTestSetup + fixture directory
cat > test/e2e/edge-async-local-storage/index.test.ts << 'TESTFILE'
import { nextTestSetup } from 'e2e-utils'
import { fetchViaHTTP } from 'next-test-utils'

describe('edge api can use async local storage', () => {
  const { next } = nextTestSetup({
    files: __dirname,
  })

  const cases = [
    {
      title: 'a single instance',
      route: '/api/single',
      expectResponse: (response: any, id: string) =>
        expect(response).toMatchObject({ status: 200, json: { id } }),
    },
    {
      title: 'multiple instances',
      route: '/api/multiple',
      expectResponse: (response: any, id: string) =>
        expect(response).toMatchObject({
          status: 200,
          json: { id: id, nestedId: `nested-${id}` },
        }),
    },
  ]

  it.each(cases)(
    'can use $title per request',
    async ({ route, expectResponse }) => {
      const ids = Array.from({ length: 100 }, (_, i) => `req-${i}`)

      const responses = await Promise.all(
        ids.map((id) =>
          fetchViaHTTP(next.url, route, {}, { headers: { 'req-id': id } }).then(
            (response) =>
              response.headers
                .get('content-type')
                ?.startsWith('application/json')
                ? response.json().then((json) => ({
                    status: response.status,
                    json,
                    text: null,
                  }))
                : response.text().then((text) => ({
                    status: response.status,
                    json: null,
                    text,
                  }))
          )
        )
      )
      const rankById = new Map(ids.map((id, rank) => [id, rank]))

      const errors: Error[] = []
      for (const [rank, response] of responses.entries()) {
        try {
          expectResponse(response, ids[rank])
        } catch (error) {
          const received = response.json?.id
          console.log(
            `response #${rank} has id from request #${rankById.get(received)}`
          )
          errors.push(error as Error)
        }
      }
      if (errors.length) {
        throw errors[0]
      }
    }
  )
})
TESTFILE

echo "Patch applied successfully."
