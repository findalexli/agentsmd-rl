import { register } from 'node:module'
import { pathToFileURL } from 'node:url'

register(new URL('./loader.mjs', import.meta.url))

const benchPath = process.argv[2]
const repoDir = process.argv[3]
if (!benchPath || !repoDir) {
  console.error('usage: extract.mjs <bench-file-abs-path> <repo-dir>')
  process.exit(2)
}
process.chdir(repoDir)

await import(pathToFileURL(benchPath).href)
const stub = await import('./vitest-stub.mjs')
console.log(JSON.stringify(stub.__calls))
