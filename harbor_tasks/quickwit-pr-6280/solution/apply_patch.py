#!/usr/bin/env python3
"""Apply the gold patch to the quickwit repository."""
import subprocess
import os

REPO = "/workspace/quickwit"
PATCHFILE = "/tmp/patch.diff"

# Read the original files and write patched versions directly
metastore_path = os.path.join(REPO, "quickwit/quickwit-metastore/src/metastore/postgres/metastore.rs")
metadata_path = os.path.join(REPO, "quickwit/quickwit-parquet-engine/src/split/metadata.rs")

with open(metastore_path, 'r') as f:
    metastore_content = f.read()

with open(metadata_path, 'r') as f:
    metadata_content = f.read()

# --- metastore.rs patches ---

# Find the DELETE_SPLITS_QUERY in delete_metrics_splits and replace it
old_query = '''        const DELETE_SPLITS_QUERY: &str = r#"
            DELETE FROM metrics_splits
            WHERE
                index_uid = $1
                AND split_id = ANY($2)
                AND split_state = 'MarkedForDeletion'
            RETURNING split_id
        "#;

        let deleted_split_ids: Vec<String> = sqlx::query_scalar(DELETE_SPLITS_QUERY)
            .bind(request.index_uid())
            .bind(&request.split_ids)
            .fetch_all(&self.connection_pool)
            .await
            .map_err(|sqlx_error| convert_sqlx_err(&request.index_uid().index_id, sqlx_error))?;

        // Log if some splits were not deleted (either non-existent or not
        // in MarkedForDeletion state). Delete is idempotent — we don't error
        // for missing splits.
        if deleted_split_ids.len() != request.split_ids.len() {
            let not_deleted: Vec<String> = request
                .split_ids
                .iter()
                .filter(|id| !deleted_split_ids.contains(id))
                .cloned()
                .collect();

            if !not_deleted.is_empty() {
                warn!(
                    index_uid = %request.index_uid(),
                    not_deleted = ?not_deleted,
                    "some metrics splits were not deleted (non-existent or not marked for deletion)"
                );
            }
        }

        info!(
            index_uid = %request.index_uid(),
            deleted_count = deleted_split_ids.len(),
            "deleted metrics splits successfully"
        );'''

new_query = '''        // Match the non-metrics delete_splits pattern: distinguish
        // "not found" (warn + succeed) from "not deletable" (FailedPrecondition).
        const DELETE_SPLITS_QUERY: &str = r#"
            WITH input_splits AS (
                SELECT input_splits.split_id, metrics_splits.split_state
                FROM UNNEST($2::text[]) AS input_splits(split_id)
                LEFT JOIN metrics_splits
                    ON metrics_splits.index_uid = $1
                    AND metrics_splits.split_id = input_splits.split_id
            ),
            deleted AS (
                DELETE FROM metrics_splits
                USING input_splits
                WHERE
                    metrics_splits.index_uid = $1
                    AND metrics_splits.split_id = input_splits.split_id
                    AND NOT EXISTS (
                        SELECT 1 FROM input_splits
                        WHERE split_state IN ('Staged', 'Published')
                    )
                RETURNING metrics_splits.split_id
            )
            SELECT
                (SELECT COUNT(*) FROM input_splits WHERE split_state IS NOT NULL) as num_found,
                (SELECT COUNT(*) FROM deleted) as num_deleted,
                COALESCE(
                    (SELECT ARRAY_AGG(split_id) FROM input_splits
                     WHERE split_state IN ('Staged', 'Published')),
                    ARRAY[]::text[]
                ) as not_deletable,
                COALESCE(
                    (SELECT ARRAY_AGG(split_id) FROM input_splits
                     WHERE split_state IS NULL),
                    ARRAY[]::text[]
                ) as not_found
        "#;

        let (num_found, num_deleted, not_deletable_ids, not_found_ids): (
            i64,
            i64,
            Vec<String>,
            Vec<String>,
        ) = sqlx::query_as(DELETE_SPLITS_QUERY)
            .bind(request.index_uid())
            .bind(&request.split_ids)
            .fetch_one(&self.connection_pool)
            .await
            .map_err(|sqlx_error| convert_sqlx_err(&request.index_uid().index_id, sqlx_error))?;

        if !not_deletable_ids.is_empty() {
            let message = format!(
                "splits `{}` are not deletable",
                not_deletable_ids.join(", ")
            );
            let entity = EntityKind::Splits {
                split_ids: not_deletable_ids,
            };
            return Err(MetastoreError::FailedPrecondition { entity, message });
        }

        if !not_found_ids.is_empty() {
            warn!(
                index_uid = %request.index_uid(),
                not_found = ?not_found_ids,
                "{} metrics splits were not found and could not be deleted",
                not_found_ids.len()
            );
        }

        let _ = (num_found, num_deleted); // used by the CTE logic

        info!(
            index_uid = %request.index_uid(),
            num_deleted,
            "deleted metrics splits successfully"
        );'''

if old_query in metastore_content:
    metastore_content = metastore_content.replace(old_query, new_query)
    print("Metastore patch applied successfully")
else:
    print("ERROR: Could not find old_query in metastore.rs")
    print("Looking for DELETE_SPLITS_QUERY in delete_metrics_splits...")
    idx = metastore_content.find("async fn delete_metrics_splits")
    if idx >= 0:
        chunk = metastore_content[idx:idx+2000]
        print(f"Found delete_metrics_splits at {idx}")
        print(chunk[:500])
    exit(1)

# --- metadata.rs patch ---
old_doc = "    /// RowKeys (sort-key min/max boundaries) as proto bytes."
new_doc = "    /// RowKeys (sort-key min/max boundaries) as serialized proto bytes\n    /// (`sortschema::RowKeys` in `event_store_sortschema.proto`)."

if old_doc in metadata_content:
    metadata_content = metadata_content.replace(old_doc, new_doc)
    print("Metadata patch applied successfully")
else:
    print("ERROR: Could not find old_doc in metadata.rs")
    exit(1)

# Write the patched files
with open(metastore_path, 'w') as f:
    f.write(metastore_content)

with open(metadata_path, 'w') as f:
    f.write(metadata_content)

# Verify the patches
with open(metastore_path, 'r') as f:
    content = f.read()
    if "splits `{}` are not deletable" in content:
        print("Verification passed: metastore.rs patched correctly")
    else:
        print("ERROR: metastore.rs verification failed")
        exit(1)

with open(metadata_path, 'r') as f:
    content = f.read()
    if "sortschema::RowKeys" in content and "event_store_sortschema.proto" in content:
        print("Verification passed: metadata.rs patched correctly")
    else:
        print("ERROR: metadata.rs verification failed")
        exit(1)

print("All patches applied and verified successfully")