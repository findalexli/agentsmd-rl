#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wheels

# Idempotency guard
if grep -qF "return findAll(where=\"createdat >= '#local.startOfMonth#'\");" "templates/base/src/app/CLAUDE.md" && grep -qF "local.where = \"name LIKE '%#params.q#%' OR description LIKE '%#params.q#%'\";" "templates/base/src/app/controllers/CLAUDE.md" && grep -qF "where=\"status = 'pending' AND runAt <= now()\"," "templates/base/src/app/jobs/CLAUDE.md" && grep -qF "while (model(\"Article\").findOne(where = \"slug = '#this.slug#' AND id != #this.id" "templates/base/src/app/lib/CLAUDE.md" && grep -qF "local.user = model(\"User\").findOne(where = \"email = '#params.email#'\");" "templates/base/src/app/mailers/CLAUDE.md" && grep -qF "where=\"(email = '#arguments.identifier#' OR username = '#arguments.identifier#')" "templates/base/src/app/models/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/templates/base/src/app/CLAUDE.md b/templates/base/src/app/CLAUDE.md
@@ -300,7 +300,7 @@ component extends="Model" {
     
     function findThisMonth() {
         local.startOfMonth = CreateDate(Year(Now()), Month(Now()), 1);
-        return findAll(where="createdat >= ?", whereParams=[local.startOfMonth]);
+        return findAll(where="createdat >= '#local.startOfMonth#'");
     }
 
     // Business logic methods
diff --git a/templates/base/src/app/controllers/CLAUDE.md b/templates/base/src/app/controllers/CLAUDE.md
@@ -413,8 +413,7 @@ function index() {
     // With search filtering
     if (StructKeyExists(params, "q") && len(params.q)) {
         products = model("Product").findAll(
-            where="name LIKE ? OR description LIKE ?",
-            whereParams=["%#params.q#%", "%#params.q#%"],
+            where="name LIKE '%#params.q#%' OR description LIKE '%#params.q#%'",
             page=params.page ?: 1,
             perPage=25
         );
@@ -508,25 +507,21 @@ function index() {
 #### Search and Filtering
 ```cfc
 function search() {
-    searchCriteria = {};
-    
-    // Build dynamic where clause
-    if (len(params.q ?: "")) {
-        searchCriteria.where = "name LIKE ? OR description LIKE ?";
-        searchCriteria.whereParams = ["%#params.q#%", "%#params.q#%"];
+    local.where = "";
+
+    // Build where clause
+    if (Len(params.q ?: "")) {
+        local.where = "name LIKE '%#params.q#%' OR description LIKE '%#params.q#%'";
     }
-    
-    if (isNumeric(params.categoryId ?: "")) {
-        local.where = searchCriteria.where ?: "";
-        if (len(local.where)) local.where &= " AND ";
-        local.where &= "categoryId = ?";
-        
-        searchCriteria.where = local.where;
-        searchCriteria.whereParams = searchCriteria.whereParams ?: [];
-        arrayAppend(searchCriteria.whereParams, params.categoryId);
+
+    if (IsNumeric(params.categoryId ?: "")) {
+        if (Len(local.where)) {
+            local.where &= " AND ";
+        }
+        local.where &= "categoryId = #params.categoryId#";
     }
-    
-    products = model("Product").findAll(argumentCollection=searchCriteria);
+
+    products = model("Product").findAll(where = local.where);
 }
 ```
 
diff --git a/templates/base/src/app/jobs/CLAUDE.md b/templates/base/src/app/jobs/CLAUDE.md
@@ -258,8 +258,7 @@ component extends="wheels.Job" {
                 
             // Get pending orders
             local.pendingOrders = model("Order").findAll(
-                where="status = ?",
-                whereParams=["pending"],
+                where="status = 'pending'",
                 order="createdAt",
                 maxRows=local.batchSize
             );
@@ -463,8 +462,7 @@ component extends="wheels.Job" {
     
     private numeric function cleanupAuditLogs(required date cutoffDate) {
         local.deleted = model("AuditLog").deleteAll(
-            where="createdAt < ?",
-            whereParams=[arguments.cutoffDate]
+            where="createdAt < '#arguments.cutoffDate#'"
         );
         
         logInfo("Deleted #local.deleted# old audit log entries");
@@ -677,8 +675,7 @@ function processJobQueue() {
     try {
         // Get jobs from database queue
         local.jobs = model("QueuedJob").findAll(
-            where="status = ? AND runAt <= ?",
-            whereParams=["pending", now()],
+            where="status = 'pending' AND runAt <= now()",
             order="priority DESC, createdAt",
             maxRows=10
         );
@@ -794,8 +791,7 @@ component {
     
     function processScheduledJobs() {
         local.dueJobs = model("ScheduledJob").findAll(
-            where="enabled = ? AND nextRun <= ?",
-            whereParams=[true, now()]
+            where="enabled = true AND nextRun <= now()"
         );
         
         for (local.job in local.dueJobs) {
diff --git a/templates/base/src/app/lib/CLAUDE.md b/templates/base/src/app/lib/CLAUDE.md
@@ -1004,7 +1004,7 @@ component extends="Model" {
             local.counter = 1;
             local.originalSlug = this.slug;
             
-            while (model("Article").findOne(where="slug = ? AND id != ?", whereParams=[this.slug, this.id ?: 0])) {
+            while (model("Article").findOne(where = "slug = '#this.slug#' AND id != #this.id ?: 0#")) {
                 this.slug = local.originalSlug & "-" & local.counter;
                 local.counter++;
             }
diff --git a/templates/base/src/app/mailers/CLAUDE.md b/templates/base/src/app/mailers/CLAUDE.md
@@ -1035,7 +1035,7 @@ component extends="Controller" {
     }
 
     function requestPasswordReset() {
-        local.user = model("User").findOne(where = "email = ?", whereParams = [params.email]);
+        local.user = model("User").findOne(where = "email = '#params.email#'");
 
         if (isObject(local.user)) {
             // Generate reset token
@@ -1115,8 +1115,7 @@ component extends="wheels.Job" {
             
             // Get active subscribers
             local.subscribers = model("Subscriber").findAll(
-                where = "active = ? AND subscriptionType IN (?)",
-                whereParams = [true, "newsletter,all"]
+                where = "active = true AND subscriptionType IN ('newsletter','all')"
             );
 
             local.newsletterMailer = createObject("component", "mailers.NewsletterMailer");
diff --git a/templates/base/src/app/models/CLAUDE.md b/templates/base/src/app/models/CLAUDE.md
@@ -274,7 +274,7 @@ component extends="Model" {
      * Find products in specific category
      */
     function findInCategory(required numeric categoryid) {
-        return findAll(where="categoryid = ?", whereParams=[arguments.categoryid]);
+        return findAll(where="categoryid = '#arguments.categoryid#'");
     }
     
     /**
@@ -336,7 +336,7 @@ component extends="Model" {
         // Ensure uniqueness
         local.counter = 1;
         local.originalSlug = local.slug;
-        while (model("Product").exists(where="slug = ? AND id != ?", whereParams=[local.slug, this.id ?: 0])) {
+        while (model("Product").exists(where="slug = '#local.slug#' AND id != '#this.id ?: 0#'")) {
             local.slug = local.originalSlug & "-" & local.counter;
             local.counter++;
         }
@@ -519,14 +519,14 @@ component extends="Model" {
      * Find posts by specific author
      */
     function findByAuthor(required numeric authorid) {
-        return findAll(where="authorid = ?", whereParams=[arguments.authorid]);
+        return findAll(where="authorid = '#arguments.authorid#'");
     }
     
     /**
      * Find posts in date range
      */
     function findInDateRange(required date startDate, required date endDate) {
-        return findAll(where="publishedAt BETWEEN ? AND ?", whereParams=[arguments.startDate, arguments.endDate]);
+        return findAll(where="publishedAt BETWEEN '#arguments.startDate#' AND '#arguments.endDate#'");
     }
     
     // Callback methods
@@ -589,7 +589,7 @@ component extends="Model" {
         // Ensure uniqueness
         local.counter = 1;
         local.originalSlug = local.slug;
-        while (model("Post").exists(where="slug = ? AND id != ?", whereParams=[local.slug, this.id ?: 0])) {
+        while (model("Post").exists(where="slug = '#local.slug#' AND id != '#this.id ?: 0#'")) {
             local.slug = local.originalSlug & "-" & local.counter;
             local.counter++;
         }
@@ -661,8 +661,7 @@ component extends="Model" {
     static function authenticate(required string identifier, required string password) {
         // Find user by email or username
         local.user = model("User").findOne(
-            where="(email = ? OR username = ?) AND deletedat IS NULL",
-            whereParams=[arguments.identifier, arguments.identifier]
+            where="(email = '#arguments.identifier#' OR username = '#arguments.identifier#') AND deletedat IS NULL"
         );
         
         if (!isObject(local.user)) {
@@ -726,15 +725,15 @@ component extends="Model" {
      * Check if user has specific role
      */
     function hasRole(required string roleName) {
-        return this.roles().exists(where="name = ?", whereParams=[arguments.roleName]);
+        return this.roles().exists(where="name = '#arguments.roleName#'");
     }
     
     /**
      * Check if user has any of the specified roles
      */
     function hasAnyRole(required string roleNames) {
         local.roleList = listToArray(arguments.roleNames);
-        return this.roles().exists(where="name IN (?)", whereParams=[roleList]);
+        return this.roles().exists(where="name IN (#roleList#)");
     }
     
     /**
@@ -743,14 +742,14 @@ component extends="Model" {
     function hasPermission(required string permission) {
         return this.roles().joins("INNER JOIN rolePermissions rp ON roles.id = rp.roleid")
                           .joins("INNER JOIN permissions p ON rp.permissionId = p.id")
-                          .exists(where="p.name = ?", whereParams=[arguments.permission]);
+                          .exists(where="p.name = '#arguments.permission#'");
     }
     
     /**
      * Add role to user
      */
     function addRole(required string roleName) {
-        local.role = model("Role").findOne(where="name = ?", whereParams=[arguments.roleName]);
+        local.role = model("Role").findOne(where="name = '#arguments.roleName#'");
         if (isObject(local.role) && !this.hasRole(arguments.roleName)) {
             model("UserRole").create(userid=this.id, roleid=local.role.id);
         }
@@ -760,9 +759,9 @@ component extends="Model" {
      * Remove role from user
      */
     function removeRole(required string roleName) {
-        local.role = model("Role").findOne(where="name = ?", whereParams=[arguments.roleName]);
+        local.role = model("Role").findOne(where="name = '#arguments.roleName#'");
         if (isObject(local.role)) {
-            model("UserRole").deleteAll(where="userid = ? AND roleid = ?", whereParams=[this.id, local.role.id]);
+            model("UserRole").deleteAll(where="userid = '#this.id#' AND roleid = '#local.role.id#'");
         }
     }
     
@@ -827,7 +826,7 @@ component extends="Model" {
         this.save();
         
         // Clean up old login attempts
-        this.loginAttempts().deleteAll(where="createdat < ?", whereParams=[dateAdd("d", -7, now())]);
+        this.loginAttempts().deleteAll(where="createdat < '#dateAdd("d", -7, now())#'");
     }
     
     /**
@@ -872,8 +871,7 @@ component extends="Model" {
     function findWithRole(required string roleName) {
         return findAll(
             include="userRoles(role)", 
-            where="roles.name = ?", 
-            whereParams=[arguments.roleName]
+            where="roles.name = '#arguments.roleName#'"
         );
     }
     
@@ -1086,7 +1084,7 @@ post = model("Post").findByKey(1);
 comments = post.comments();
 
 // Get comments with conditions
-recentComments = post.comments(where="createdat > ?", whereParams=[dateAdd("d", -7, now())]);
+recentComments = post.comments(where="createdat > '#dateAdd("d", -7, now())#'");
 
 // Count comments
 commentCount = post.commentCount();
@@ -1335,7 +1333,7 @@ component extends="Model" {
     
     private void function checkReferences() {
         // Prevent deletion if referenced by other records
-        if (model("Order").exists(where="customerId = ?", whereParams=[this.id])) {
+        if (model("Order").exists(where="customerId = '#this.id#'")) {
             throw(type="ReferentialIntegrityError", message="Cannot delete customer with existing orders");
         }
     }
@@ -1611,8 +1609,7 @@ component extends="Model" {
     function getRecentPostTitles(numeric days = 7) {
         return this.findAll(
             select="id, title, createdat",
-            where="createdat > ?",
-            whereParams=[dateAdd("d", -arguments.days, now())],
+            where="createdat > '#dateAdd("d", -arguments.days, now())#'",
             order="createdat DESC"
         );
     }
@@ -1633,8 +1630,7 @@ component extends="Model" {
      */
     function hasRecentActivity(numeric days = 30) {
         return this.posts().exists(
-            where="createdat > ?",
-            whereParams=[dateAdd("d", -arguments.days, now())]
+            where="createdat > '#dateAdd("d", -arguments.days, now())#'"
         );
     }
 }
@@ -2289,8 +2285,7 @@ totalRecords = paginationInfo.totalRecords;
 ```cfm
 // Paginated search results
 searchResults = model("Product").findAll(
-    where="name LIKE ? OR description LIKE ?",
-    whereParams=["%#params.q#%", "%#params.q#%"],
+    where="name LIKE '%#params.q#%' OR description LIKE '%#params.q#%'",
     page=params.page ?: 1,
     perPage=24,
     order="name"
@@ -2361,8 +2356,8 @@ topCustomers = model("Customer").findBySQL("
 ### Boolean Existence Checks
 ```cfm
 // More efficient than count() > 0
-hasOrders = model("Customer").exists(where="id = ?", whereParams=[customerId]);
-hasRecentActivity = model("User").posts().exists(where="createdat > ?", whereParams=[lastWeek]);
+hasOrders = model("Customer").exists(where="id = '#customerId#'");
+hasRecentActivity = model("User").posts().exists(where="createdat > '#lastWeek#'");
 ```
 
 ### Query Optimization with Includes and Select
@@ -2373,8 +2368,7 @@ posts = model("Post").findAll(include="author,category,tags");
 // Limit columns to reduce data transfer
 recentTitles = model("Post").findAll(
     select="id, title, createdat",
-    where="createdat > ?",
-    whereParams=[dateAdd("d", -7, now())],
+    where="createdat > '#dateAdd("d", -7, now())#'",
     order="createdat DESC"
 );
 ```
PATCH

echo "Gold patch applied."
