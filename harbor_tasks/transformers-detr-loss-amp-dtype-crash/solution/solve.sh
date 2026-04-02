#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if the fix is already applied, skip
if grep -q 'neg_weights = prob\.pow(gamma)\.to(dtype)' src/transformers/loss/loss_lw_detr.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/loss/loss_lw_detr.py b/src/transformers/loss/loss_lw_detr.py
index dbb81b8a3d4e..0348fd3a7180 100644
--- a/src/transformers/loss/loss_lw_detr.py
+++ b/src/transformers/loss/loss_lw_detr.py
@@ -112,6 +112,7 @@ def loss_labels(self, outputs, targets, indices, num_boxes):
         if "logits" not in outputs:
             raise KeyError("No logits were found in the outputs")
         source_logits = outputs["logits"]
+        dtype = source_logits.dtype

         idx = self._get_source_permutation_idx(indices)
         target_classes_o = torch.cat([t["class_labels"][J] for t, (_, J) in zip(targets, indices)])
@@ -123,21 +124,20 @@ def loss_labels(self, outputs, targets, indices, num_boxes):
             box_iou(center_to_corners_format(src_boxes.detach()), center_to_corners_format(target_boxes))[0]
         )
         # Convert to the same dtype as the source logits as box_iou upcasts to float32
-        iou_targets = iou_targets.to(source_logits.dtype)
+        iou_targets = iou_targets.to(dtype)
         pos_ious = iou_targets.clone().detach()
         prob = source_logits.sigmoid()
         # init positive weights and negative weights
         pos_weights = torch.zeros_like(source_logits)
-        neg_weights = prob**gamma
+        # pow promotes to float32 under float16 CUDA autocast; cast back to preserve original dtype
+        neg_weights = prob.pow(gamma).to(dtype)
+        pos_ind = idx + (target_classes_o,)

-        pos_ind = list(idx)
-        pos_ind.append(target_classes_o)
+        pos_quality = prob[pos_ind].pow(alpha) * pos_ious.pow(1 - alpha)
+        pos_quality = torch.clamp(pos_quality, 0.01).detach().to(dtype)

-        t = prob[pos_ind].pow(alpha) * pos_ious.pow(1 - alpha)
-        t = torch.clamp(t, 0.01).detach()
-
-        pos_weights[pos_ind] = t
-        neg_weights[pos_ind] = 1 - t
+        pos_weights[pos_ind] = pos_quality
+        neg_weights[pos_ind] = 1 - pos_quality
         loss_ce = -pos_weights * prob.log() - neg_weights * (1 - prob).log()
         loss_ce = loss_ce.sum() / num_boxes
         losses = {"loss_ce": loss_ce}
diff --git a/src/transformers/loss/loss_rt_detr.py b/src/transformers/loss/loss_rt_detr.py
index 8f1c525bddaf..cf6d6ad05940 100644
--- a/src/transformers/loss/loss_rt_detr.py
+++ b/src/transformers/loss/loss_rt_detr.py
@@ -175,6 +175,7 @@ def loss_labels_vfl(self, outputs, targets, indices, num_boxes, log=True):
         ious = torch.diag(ious)

         src_logits = outputs["logits"]
+        dtype = src_logits.dtype
         target_classes_original = torch.cat([_target["class_labels"][i] for _target, (_, i) in zip(targets, indices)])
         target_classes = torch.full(
             src_logits.shape[:2], self.num_classes, dtype=torch.int64, device=src_logits.device
@@ -182,12 +183,13 @@ def loss_labels_vfl(self, outputs, targets, indices, num_boxes, log=True):
         target_classes[idx] = target_classes_original
         target = F.one_hot(target_classes, num_classes=self.num_classes + 1)[..., :-1]

-        target_score_original = torch.zeros_like(target_classes, dtype=src_logits.dtype)
-        target_score_original[idx] = ious.to(target_score_original.dtype)
+        target_score_original = torch.zeros_like(target_classes, dtype=dtype)
+        target_score_original[idx] = ious.to(dtype)
         target_score = target_score_original.unsqueeze(-1) * target

         pred_score = F.sigmoid(src_logits.detach())
-        weight = self.alpha * pred_score.pow(self.gamma) * (1 - target) + target_score
+        # pow promotes to float32 under float16 CUDA autocast; cast back to preserve original dtype
+        weight = (self.alpha * pred_score.pow(self.gamma) * (1 - target) + target_score).to(dtype)

         loss = F.binary_cross_entropy_with_logits(src_logits, target_score, weight=weight, reduction="none")
         loss = loss.mean(1).sum() * src_logits.shape[1] / num_boxes

PATCH

echo "Patch applied successfully."
