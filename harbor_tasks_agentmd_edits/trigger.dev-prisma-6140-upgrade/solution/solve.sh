#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if grep -q 'output.*"../generated/prisma"' internal-packages/database/prisma/schema.prisma 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Update schema.prisma: add output directory, remove tracing preview ---
python3 -c "
import re
p = 'internal-packages/database/prisma/schema.prisma'
t = open(p).read()
# Add output line after provider
t = t.replace(
    'provider        = \"prisma-client-js\"',
    'provider        = \"prisma-client-js\"\n  output          = \"../generated/prisma\"'
)
# Remove tracing from previewFeatures
t = t.replace('previewFeatures = [\"tracing\", \"metrics\"]', 'previewFeatures = [\"metrics\"]')
open(p, 'w').write(t)
"

# --- 2. Update database index.ts: export from generated path ---
sed -i 's|export \* from "@prisma/client"|export * from "../generated/prisma"|' \
    internal-packages/database/src/index.ts

# --- 3. Rewrite transaction.ts for Prisma 6 compatibility ---
cat > internal-packages/database/src/transaction.ts << 'TXEOF'
import { PrismaClient } from "../generated/prisma";
import { Decimal } from "decimal.js";
import { PrismaClientKnownRequestError } from "@prisma/client/runtime/library";

// Define the isolation levels manually
type TransactionIsolationLevel =
  | "ReadUncommitted"
  | "ReadCommitted"
  | "RepeatableRead"
  | "Serializable";

export type PrismaTransactionClient = Omit<
  PrismaClient,
  "$connect" | "$disconnect" | "$on" | "$transaction" | "$use" | "$extends"
>;

export type PrismaClientOrTransaction = PrismaClient | PrismaTransactionClient;

export type PrismaReplicaClient = Omit<PrismaClient, "$transaction">;

export { Decimal };

function isTransactionClient(prisma: PrismaClientOrTransaction): prisma is PrismaTransactionClient {
  return !("$transaction" in prisma);
}

export function isPrismaKnownError(error: unknown): error is PrismaClientKnownRequestError {
  return (
    typeof error === "object" && error !== null && "code" in error && typeof error.code === "string"
  );
}

/*
•	P2024: Connection timeout errors
•	P2028: Transaction timeout errors
•	P2034: Transaction deadlock/conflict errors
*/
const retryCodes = ["P2024", "P2028", "P2034"];

export function isPrismaRetriableError(error: unknown): boolean {
  if (!isPrismaKnownError(error)) {
    return false;
  }

  return retryCodes.includes(error.code);
}

/*
•	P2025: Record not found errors (in race conditions) [not included for now]
*/
export function isPrismaRaceConditionError(error: unknown): boolean {
  if (!isPrismaKnownError(error)) {
    return false;
  }

  return error.code === "P2025";
}

export type PrismaTransactionOptions = {
  /** The maximum amount of time (in ms) Prisma Client will wait to acquire a transaction from the database. The default value is 2000ms. */
  maxWait?: number;

  /** The maximum amount of time (in ms) the interactive transaction can run before being canceled and rolled back. The default value is 5000ms. */
  timeout?: number;

  /**  Sets the transaction isolation level. By default this is set to the value currently configured in your database. */
  isolationLevel?: TransactionIsolationLevel;

  swallowPrismaErrors?: boolean;

  /**
   * The maximum number of times the transaction will be retried in case of a serialization failure. The default value is 0.
   *
   * See https://www.prisma.io/docs/orm/prisma-client/queries/transactions#transaction-timing-issues
   */
  maxRetries?: number;
};

export async function $transaction<R>(
  prisma: PrismaClientOrTransaction,
  fn: (prisma: PrismaTransactionClient) => Promise<R>,
  prismaError: (error: PrismaClientKnownRequestError) => void,
  options?: PrismaTransactionOptions,
  attempt = 0
): Promise<R | undefined> {
  if (isTransactionClient(prisma)) {
    return fn(prisma);
  }

  try {
    return await (prisma as PrismaClient).$transaction(fn, options);
  } catch (error) {
    if (isPrismaKnownError(error)) {
      if (
        retryCodes.includes(error.code) &&
        typeof options?.maxRetries === "number" &&
        attempt < options.maxRetries
      ) {
        return $transaction(prisma, fn, prismaError, options, attempt + 1);
      }

      prismaError(error);

      if (options?.swallowPrismaErrors) {
        return;
      }
    }

    throw error;
  }
}

export function isUniqueConstraintError<T extends readonly string[]>(
  error: unknown,
  columns: T
): boolean {
  if (!isPrismaKnownError(error)) {
    return false;
  }

  if (error.code !== "P2002") {
    return false;
  }

  const target = error.meta?.target;

  if (!Array.isArray(target)) {
    return false;
  }

  if (target.length !== columns.length) {
    return false;
  }

  for (let i = 0; i < columns.length; i++) {
    if (target[i] !== columns[i]) {
      return false;
    }
  }

  return true;
}
TXEOF

# --- 4. Create query performance monitor ---
cat > apps/webapp/app/utils/queryPerformanceMonitor.server.ts << 'QPMEOF'
import { env } from "~/env.server";
import { logger } from "~/services/logger.server";

export interface QueryPerformanceConfig {
  verySlowQueryThreshold?: number; // ms
  maxQueryLogLength: number;
}

export class QueryPerformanceMonitor {
  private config: QueryPerformanceConfig;

  constructor(config: Partial<QueryPerformanceConfig> = {}) {
    this.config = {
      maxQueryLogLength: 1000,
      ...config,
    };
  }

  onQuery(
    clientType: "writer" | "replica",
    log: {
      duration: number;
      query: string;
      params: string;
      target: string;
      timestamp: Date;
    }
  ) {
    if (this.config.verySlowQueryThreshold === undefined) {
      return;
    }

    const { duration, query, params, target, timestamp } = log;

    // Only log very slow queries as errors
    if (duration > this.config.verySlowQueryThreshold) {
      // Truncate long queries for readability
      const truncatedQuery =
        query.length > this.config.maxQueryLogLength
          ? query.substring(0, this.config.maxQueryLogLength) + "..."
          : query;

      logger.error("Prisma: very slow database query", {
        clientType,
        durationMs: duration,
        query: truncatedQuery,
        target,
        timestamp,
        paramCount: this.countParams(query),
        hasParams: params !== "[]" && params !== "",
      });
    }
  }

  private countParams(query: string): number {
    // Count the number of $1, $2, etc. parameters in the query
    const paramMatches = query.match(/\$\d+/g);
    return paramMatches ? paramMatches.length : 0;
  }
}

export const queryPerformanceMonitor = new QueryPerformanceMonitor({
  verySlowQueryThreshold: env.VERY_SLOW_QUERY_THRESHOLD_MS,
});
QPMEOF

# --- 5. Add VERY_SLOW_QUERY_THRESHOLD_MS to env.server.ts ---
sed -i '/EVENT_LOOP_MONITOR_THRESHOLD_MS: z\.coerce\.number()\.int()\.default(100),/a\\n  VERY_SLOW_QUERY_THRESHOLD_MS: z.coerce.number().int().optional(),' \
    apps/webapp/app/env.server.ts

# --- 6. Update db.server.ts imports and add query monitor ---
# Add queryPerformanceMonitor import
sed -i '/^import { Span } from "@opentelemetry\/api";$/a\import { queryPerformanceMonitor } from "./utils/queryPerformanceMonitor.server";' \
    apps/webapp/app/db.server.ts

# Fix type imports for Prisma 6 (add 'type' keyword)
sed -i 's/^  PrismaClientOrTransaction,$/  type PrismaClientOrTransaction,/' apps/webapp/app/db.server.ts
sed -i 's/^  PrismaReplicaClient,$/  type PrismaReplicaClient,/' apps/webapp/app/db.server.ts
sed -i 's/^  PrismaTransactionClient,$/  type PrismaTransactionClient,/' apps/webapp/app/db.server.ts
sed -i 's/^  PrismaTransactionOptions,$/  type PrismaTransactionOptions,/' apps/webapp/app/db.server.ts

# Move $transaction import into the main import block
sed -i '/^import { \$transaction as transac } from "@trigger\.dev\/database";$/d' \
    apps/webapp/app/db.server.ts
sed -i '/^  Prisma,$/a\  $transaction as transac,' apps/webapp/app/db.server.ts

# --- 7. Update cursor rules to reference Prisma 6.14.0 ---
sed -i 's/Prisma 5\.4\.1/Prisma 6.14.0/g' .cursor/rules/webapp.mdc

# --- 8. Update package.json versions ---
python3 -c "
import json
p = 'internal-packages/database/package.json'
d = json.loads(open(p).read())
d['dependencies']['@prisma/client'] = '6.14.0'
d['dependencies']['decimal.js'] = '^10.6.0'
if 'devDependencies' not in d: d['devDependencies'] = {}
d['devDependencies']['prisma'] = '6.14.0'
d['devDependencies']['@types/decimal.js'] = '^7.4.3'
open(p, 'w').write(json.dumps(d, indent=2) + '\n')
"

# --- 9. Update .gitignore and .dockerignore ---
echo -e '\ngenerated/prisma' >> internal-packages/database/.gitignore
sed -i '/*\*\/node_modules/a\\n**/generated/prisma' .dockerignore

# --- 10. Update decompressContent to use Uint8Array ---
sed -i 's/function decompressContent(compressedBuffer: Buffer)/function decompressContent(compressedBuffer: Uint8Array)/' \
    'apps/webapp/app/routes/api.v1.projects.$projectRef.background-workers.$envSlug.$version.ts'
sed -i "s/const decodedBuffer = Buffer.from(compressedBuffer.toString(\"utf-8\"), \"base64\");/const decodedBuffer = Buffer.from(Buffer.from(compressedBuffer).toString(\"utf-8\"), \"base64\");/" \
    'apps/webapp/app/routes/api.v1.projects.$projectRef.background-workers.$envSlug.$version.ts'

echo "Patch applied successfully."
