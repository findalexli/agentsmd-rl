#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied
if grep -q "import { literal } from '@supabase/pg-meta/src/pg-format'" apps/studio/data/database-queues/database-queue-messages-send-mutation.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/apps/studio/data/database-queues/database-queue-messages-archive-mutation.ts b/apps/studio/data/database-queues/database-queue-messages-archive-mutation.ts
index f4f92aaa36157..7fbf8082e320a 100644
--- a/apps/studio/data/database-queues/database-queue-messages-archive-mutation.ts
+++ b/apps/studio/data/database-queues/database-queue-messages-archive-mutation.ts
@@ -1,9 +1,10 @@
+import { literal } from '@supabase/pg-meta/src/pg-format'
 import { useMutation, useQueryClient } from '@tanstack/react-query'
-import { toast } from 'sonner'
-
 import { isQueueNameValid } from 'components/interfaces/Integrations/Queues/Queues.utils'
 import { executeSql } from 'data/sql/execute-sql-query'
+import { toast } from 'sonner'
 import type { ResponseError, UseCustomMutationOptions } from 'types'
+
 import { databaseQueuesKeys } from './keys'

 export type DatabaseQueueMessageArchiveVariables = {
@@ -27,7 +28,7 @@ export async function archiveDatabaseQueueMessage({
   const { result } = await executeSql({
     projectRef,
     connectionString,
-    sql: `SELECT * FROM pgmq.archive('${queueName}', ${messageId})`,
+    sql: `SELECT * FROM pgmq.archive(${literal(queueName)}, ${literal(messageId)})`,
     queryKey: databaseQueuesKeys.create(),
   })

diff --git a/apps/studio/data/database-queues/database-queue-messages-delete-mutation.ts b/apps/studio/data/database-queues/database-queue-messages-delete-mutation.ts
index 28b9d817556bb..348a3f672c8a8 100644
--- a/apps/studio/data/database-queues/database-queue-messages-delete-mutation.ts
+++ b/apps/studio/data/database-queues/database-queue-messages-delete-mutation.ts
@@ -1,9 +1,10 @@
+import { literal } from '@supabase/pg-meta/src/pg-format'
 import { useMutation, useQueryClient } from '@tanstack/react-query'
-import { toast } from 'sonner'
-
 import { isQueueNameValid } from 'components/interfaces/Integrations/Queues/Queues.utils'
 import { executeSql } from 'data/sql/execute-sql-query'
+import { toast } from 'sonner'
 import type { ResponseError, UseCustomMutationOptions } from 'types'
+
 import { databaseQueuesKeys } from './keys'

 export type DatabaseQueueMessageDeleteVariables = {
@@ -28,7 +29,7 @@ export async function deleteDatabaseQueueMessage({
   const { result } = await executeSql({
     projectRef,
     connectionString,
-    sql: `SELECT * FROM pgmq.delete('${queueName}', ${messageId})`,
+    sql: `SELECT * FROM pgmq.delete(${literal(queueName)}, ${literal(messageId)})`,
     queryKey: databaseQueuesKeys.create(),
   })

diff --git a/apps/studio/data/database-queues/database-queue-messages-infinite-query.ts b/apps/studio/data/database-queues/database-queue-messages-infinite-query.ts
index cf382f5755918..7cac5705bd37b 100644
--- a/apps/studio/data/database-queues/database-queue-messages-infinite-query.ts
+++ b/apps/studio/data/database-queues/database-queue-messages-infinite-query.ts
@@ -1,12 +1,13 @@
+import { literal } from '@supabase/pg-meta/src/pg-format'
 import { InfiniteData, useInfiniteQuery } from '@tanstack/react-query'
-import dayjs from 'dayjs'
-import { last } from 'lodash'
-
 import { isQueueNameValid } from 'components/interfaces/Integrations/Queues/Queues.utils'
 import { QUEUE_MESSAGE_TYPE } from 'components/interfaces/Integrations/Queues/SingleQueue/Queue.utils'
 import { executeSql } from 'data/sql/execute-sql-query'
+import dayjs from 'dayjs'
 import { DATE_FORMAT } from 'lib/constants'
+import { last } from 'lodash'
 import type { ResponseError, UseCustomInfiniteQueryOptions } from 'types'
+
 import { databaseQueuesKeys } from './keys'

 export type DatabaseQueueVariables = {
@@ -67,7 +68,7 @@ export async function getDatabaseQueue({
         ${[queueQuery, archivedQuery].filter(Boolean).join(' UNION ALL ')}
       ) AS combined`
   if (afterTimestamp) {
-    query += ` WHERE enqueued_at > '${afterTimestamp}'`
+    query += ` WHERE enqueued_at > ${literal(afterTimestamp)}`
   }

   const { result } = await executeSql({
diff --git a/apps/studio/data/database-queues/database-queue-messages-send-mutation.ts b/apps/studio/data/database-queues/database-queue-messages-send-mutation.ts
index 0ad1ecf5f4dab..81ac71e3bd120 100644
--- a/apps/studio/data/database-queues/database-queue-messages-send-mutation.ts
+++ b/apps/studio/data/database-queues/database-queue-messages-send-mutation.ts
@@ -1,9 +1,10 @@
+import { literal } from '@supabase/pg-meta/src/pg-format'
 import { useMutation, useQueryClient } from '@tanstack/react-query'
-import { toast } from 'sonner'
-
 import { isQueueNameValid } from 'components/interfaces/Integrations/Queues/Queues.utils'
 import { executeSql } from 'data/sql/execute-sql-query'
+import { toast } from 'sonner'
 import type { ResponseError, UseCustomMutationOptions } from 'types'
+
 import { databaseQueuesKeys } from './keys'

 export type DatabaseQueueMessageSendVariables = {
@@ -30,7 +31,7 @@ export async function sendDatabaseQueueMessage({
   const { result } = await executeSql({
     projectRef,
     connectionString,
-    sql: `select * from pgmq.send( '${queueName}', '${payload}', ${delay})`,
+    sql: `select * from pgmq.send(${literal(queueName)}, ${literal(payload)}, ${literal(delay)})`,
     queryKey: databaseQueuesKeys.create(),
   })


PATCH

echo "Patch applied successfully."
