#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nixopus

# Idempotency guard
if grep -qF "You are a senior backend engineer building the Nixopus API \u2014 a production-grade " ".cursor/rules/backend.mdc" && grep -qF "You are a senior frontend engineer building the Nixopus dashboard \u2014 a modern, vi" ".cursor/rules/frontend.mdc" && grep -qF "You are a senior Python engineer building the Nixopus CLI \u2014 a production-grade c" ".cursor/rules/installer_cli.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/backend.mdc b/.cursor/rules/backend.mdc
@@ -0,0 +1,702 @@
+---
+description: Go API Development Rules for Nixopus Backend
+globs: api/**/*.go
+alwaysApply: false
+---
+
+# Nixopus Go API Development Guidelines
+
+You are a senior backend engineer building the Nixopus API — a production-grade Go application using the Fuego framework, Bun ORM, and domain-driven architecture. Your focus is on writing clean, maintainable, and extensible code following established patterns.
+
+## Core Principles
+
+### DRY (Don't Repeat Yourself) — Highest Priority
+- **Before writing new code**, search the codebase for existing implementations
+- Check `internal/utils/` for common utilities (`GetUser`, `SendErrorResponse`, `SendJSONResponse`)
+- Check `internal/types/` for shared type definitions
+- Reuse existing storage patterns and repository interfaces
+- Extract common validation logic to shared validators
+- Use existing middleware from `internal/middleware/`
+
+### Single Responsibility Principle (SRP)
+- **Controllers**: HTTP request/response handling only
+- **Services**: Business logic and orchestration
+- **Storage**: Database operations only (no business logic)
+- **Validation**: Request validation only
+- **Types**: Data structures and domain errors
+- Each file should have one primary purpose
+
+### Code Readability
+```go
+// ✅ Good: Early returns, flat structure
+func (c *Controller) HandleRequest(f fuego.ContextNoBody) (*types.Response, error) {
+    user := utils.GetUser(f.Response(), f.Request())
+    if user == nil {
+        return nil, fuego.HTTPError{Status: http.StatusUnauthorized}
+    }
+
+    data, err := c.service.GetData(user.ID.String())
+    if err != nil {
+        c.logger.Log(logger.Error, err.Error(), "")
+        return nil, fuego.HTTPError{Err: err, Status: http.StatusInternalServerError}
+    }
+
+    return &types.Response{
+        Status:  "success",
+        Message: "Data fetched successfully",
+        Data:    data,
+    }, nil
+}
+
+// ❌ Bad: Nested conditions
+func (c *Controller) HandleRequest(f fuego.ContextNoBody) (*types.Response, error) {
+    user := utils.GetUser(f.Response(), f.Request())
+    if user != nil {
+        data, err := c.service.GetData(user.ID.String())
+        if err == nil {
+            return &types.Response{Status: "success", Data: data}, nil
+        } else {
+            return nil, fuego.HTTPError{Err: err, Status: http.StatusInternalServerError}
+        }
+    }
+    return nil, fuego.HTTPError{Status: http.StatusUnauthorized}
+}
+```
+
+## Architecture
+
+### Directory Structure
+```
+api/
+├── internal/
+│   ├── features/              # Domain features
+│   │   └── [domain]/
+│   │       ├── controller/    # HTTP handlers
+│   │       │   ├── init.go    # Controller struct & constructor
+│   │       │   └── [action].go
+│   │       ├── service/       # Business logic
+│   │       │   ├── init.go    # Service struct & constructor
+│   │       │   └── [action].go
+│   │       ├── storage/       # Database operations
+│   │       │   └── init.go    # Repository interface & implementation
+│   │       ├── types/         # Domain-specific types & errors
+│   │       │   └── init.go
+│   │       ├── validation/    # Request validators
+│   │       │   └── validator.go
+│   │       └── tests/         # Unit tests
+│   ├── middleware/            # HTTP middleware
+│   ├── routes/                # Route registration
+│   ├── storage/               # Shared storage (App, Store)
+│   ├── types/                 # Shared types
+│   └── utils/                 # Shared utilities
+├── migrations/                # SQL migrations by domain
+└── templates/                 # YAML templates
+```
+
+### Creating a New Feature Domain
+
+1. Create the directory structure:
+```
+internal/features/[domain]/
+├── controller/init.go
+├── service/init.go
+├── storage/init.go
+├── types/init.go
+├── validation/validator.go
+└── tests/
+```
+
+2. Register routes in `internal/routes/[domain].go`
+3. Add middleware configuration in `internal/routes/routes.go`
+
+## Fuego Framework Patterns
+
+### Controller Structure
+```go
+package controller
+
+import (
+    "context"
+    "net/http"
+
+    "github.com/raghavyuva/nixopus-api/internal/features/[domain]/service"
+    "github.com/raghavyuva/nixopus-api/internal/features/[domain]/storage"
+    "github.com/raghavyuva/nixopus-api/internal/features/[domain]/validation"
+    "github.com/raghavyuva/nixopus-api/internal/features/logger"
+    "github.com/raghavyuva/nixopus-api/internal/features/notification"
+    shared_storage "github.com/raghavyuva/nixopus-api/internal/storage"
+    shared_types "github.com/raghavyuva/nixopus-api/internal/types"
+)
+
+type DomainController struct {
+    store        *shared_storage.Store
+    validator    *validation.Validator
+    service      *service.DomainService
+    ctx          context.Context
+    logger       logger.Logger
+    notification *notification.NotificationManager
+}
+
+func NewDomainController(
+    store *shared_storage.Store,
+    ctx context.Context,
+    l logger.Logger,
+    notificationManager *notification.NotificationManager,
+) *DomainController {
+    storage := storage.DomainStorage{DB: store.DB, Ctx: ctx}
+    return &DomainController{
+        store:        store,
+        validator:    validation.NewValidator(&storage),
+        service:      service.NewDomainService(store, ctx, l, &storage),
+        ctx:          ctx,
+        logger:       l,
+        notification: notificationManager,
+    }
+}
+```
+
+### Handler Patterns
+
+**GET Request (No Body):**
+```go
+func (c *DomainController) GetItems(f fuego.ContextNoBody) (*shared_types.Response, error) {
+    w, r := f.Response(), f.Request()
+    user := utils.GetUser(w, r)
+
+    if user == nil {
+        return nil, fuego.HTTPError{
+            Err:    nil,
+            Status: http.StatusUnauthorized,
+        }
+    }
+
+    items, err := c.service.GetItems(user.ID.String())
+    if err != nil {
+        c.logger.Log(logger.Error, err.Error(), "")
+        return nil, fuego.HTTPError{
+            Err:    err,
+            Status: http.StatusInternalServerError,
+        }
+    }
+
+    return &shared_types.Response{
+        Status:  "success",
+        Message: "Items fetched successfully",
+        Data:    items,
+    }, nil
+}
+```
+
+**POST/PUT Request (With Body):**
+```go
+func (c *DomainController) CreateItem(f fuego.ContextWithBody[types.CreateItemRequest]) (*shared_types.Response, error) {
+    w, r := f.Response(), f.Request()
+    user := utils.GetUser(w, r)
+
+    if user == nil {
+        return nil, fuego.HTTPError{Status: http.StatusUnauthorized}
+    }
+
+    body, err := f.Body()
+    if err != nil {
+        c.logger.Log(logger.Error, err.Error(), "")
+        return nil, fuego.HTTPError{Err: err, Status: http.StatusBadRequest}
+    }
+
+    if err := c.validator.ValidateRequest(&body); err != nil {
+        return nil, fuego.HTTPError{Err: err, Status: http.StatusBadRequest}
+    }
+
+    item, err := c.service.CreateItem(user.ID.String(), body)
+    if err != nil {
+        c.logger.Log(logger.Error, err.Error(), "")
+        return nil, fuego.HTTPError{Err: err, Status: http.StatusInternalServerError}
+    }
+
+    return &shared_types.Response{
+        Status:  "success",
+        Message: "Item created successfully",
+        Data:    item,
+    }, nil
+}
+```
+
+**Path Parameters:**
+```go
+func (c *DomainController) GetItem(f fuego.ContextNoBody) (*shared_types.Response, error) {
+    itemID := f.PathParam("id")
+    if itemID == "" {
+        return nil, fuego.HTTPError{
+            Err:    errors.New("item ID is required"),
+            Status: http.StatusBadRequest,
+        }
+    }
+    // ...
+}
+```
+
+**Query Parameters:**
+```go
+func (c *DomainController) ListItems(f fuego.ContextNoBody) (*shared_types.Response, error) {
+    q := f.Request().URL.Query()
+    
+    page := 1
+    if v := q.Get("page"); v != "" {
+        if p, err := strconv.Atoi(v); err == nil && p > 0 {
+            page = p
+        }
+    }
+    // ...
+}
+```
+
+## Service Layer Patterns
+
+### Service Structure
+```go
+package service
+
+import (
+    "context"
+
+    "github.com/raghavyuva/nixopus-api/internal/features/[domain]/storage"
+    "github.com/raghavyuva/nixopus-api/internal/features/logger"
+    shared_storage "github.com/raghavyuva/nixopus-api/internal/storage"
+)
+
+type DomainService struct {
+    store   *shared_storage.Store
+    ctx     context.Context
+    logger  logger.Logger
+    storage storage.DomainRepository
+}
+
+func NewDomainService(
+    store *shared_storage.Store,
+    ctx context.Context,
+    l logger.Logger,
+    repository storage.DomainRepository,
+) *DomainService {
+    return &DomainService{
+        store:   store,
+        ctx:     ctx,
+        logger:  l,
+        storage: repository,
+    }
+}
+```
+
+### Service Method Pattern
+```go
+// GetItems retrieves all items for a user.
+// Returns empty slice if no items found, error on database failure.
+func (s *DomainService) GetItems(userID string) ([]shared_types.Item, error) {
+    items, err := s.storage.GetItemsByUserID(userID)
+    if err != nil {
+        s.logger.Log(logger.Error, err.Error(), userID)
+        return nil, err
+    }
+
+    if items == nil {
+        return []shared_types.Item{}, nil
+    }
+
+    return items, nil
+}
+```
+
+## Storage Layer Patterns
+
+### Repository Interface
+```go
+package storage
+
+import (
+    "context"
+    shared_types "github.com/raghavyuva/nixopus-api/internal/types"
+    "github.com/uptrace/bun"
+)
+
+type DomainStorage struct {
+    DB  *bun.DB
+    Ctx context.Context
+}
+
+// DomainRepository defines the interface for storage operations.
+// This enables mocking in tests.
+type DomainRepository interface {
+    CreateItem(item *shared_types.Item) error
+    GetItemByID(itemID string) (*shared_types.Item, error)
+    GetItemsByUserID(userID string) ([]shared_types.Item, error)
+    UpdateItem(itemID string, updates map[string]interface{}) error
+    DeleteItem(itemID, userID string) error
+}
+```
+
+### Storage Implementation with Transactions
+```go
+// CreateItem creates a new item with transaction support.
+func (s *DomainStorage) CreateItem(item *shared_types.Item) error {
+    tx, err := s.DB.BeginTx(s.Ctx, nil)
+    if err != nil {
+        return err
+    }
+    defer tx.Rollback()
+
+    _, err = tx.NewInsert().Model(item).Exec(s.Ctx)
+    if err != nil {
+        return err
+    }
+
+    return tx.Commit()
+}
+
+// GetItemByID retrieves an item by ID, excluding soft-deleted records.
+func (s *DomainStorage) GetItemByID(itemID string) (*shared_types.Item, error) {
+    var item shared_types.Item
+    err := s.DB.NewSelect().
+        Model(&item).
+        Where("id = ? AND deleted_at IS NULL", itemID).
+        Scan(s.Ctx)
+    return &item, err
+}
+
+// DeleteItem performs a soft delete.
+func (s *DomainStorage) DeleteItem(itemID, userID string) error {
+    tx, err := s.DB.BeginTx(s.Ctx, nil)
+    if err != nil {
+        return err
+    }
+    defer tx.Rollback()
+
+    _, err = tx.NewUpdate().
+        Model((*shared_types.Item)(nil)).
+        Set("deleted_at = NOW()").
+        Set("updated_at = NOW()").
+        Where("id = ? AND user_id = ? AND deleted_at IS NULL", itemID, userID).
+        Exec(s.Ctx)
+    if err != nil {
+        return err
+    }
+
+    return tx.Commit()
+}
+```
+
+## Validation Patterns
+
+### Validator Structure
+```go
+package validation
+
+import (
+    "github.com/raghavyuva/nixopus-api/internal/features/[domain]/types"
+)
+
+// DomainRepository interface for validation dependencies
+type DomainRepository interface {
+    GetItemByID(itemID string) (*shared_types.Item, error)
+}
+
+type Validator struct {
+    storage DomainRepository
+}
+
+func NewValidator(storage DomainRepository) *Validator {
+    return &Validator{storage: storage}
+}
+
+// ValidateRequest validates request objects using type switch.
+func (v *Validator) ValidateRequest(req any) error {
+    switch r := req.(type) {
+    case *types.CreateItemRequest:
+        return v.validateCreateItemRequest(*r)
+    case *types.UpdateItemRequest:
+        return v.validateUpdateItemRequest(*r)
+    default:
+        return types.ErrInvalidRequestType
+    }
+}
+
+func (v *Validator) validateCreateItemRequest(req types.CreateItemRequest) error {
+    if req.Name == "" {
+        return types.ErrMissingName
+    }
+    if len(req.Name) > 255 {
+        return types.ErrNameTooLong
+    }
+    return nil
+}
+```
+
+## Type Definitions
+
+### Domain Types Pattern
+```go
+package types
+
+import "errors"
+
+// Request types
+type CreateItemRequest struct {
+    Name        string `json:"name"`
+    Description string `json:"description,omitempty"`
+}
+
+type UpdateItemRequest struct {
+    ID          string `json:"id"`
+    Name        string `json:"name,omitempty"`
+    Description string `json:"description,omitempty"`
+}
+
+// Domain-specific errors
+var (
+    ErrMissingName       = errors.New("name is required")
+    ErrNameTooLong       = errors.New("name exceeds maximum length")
+    ErrInvalidRequestType = errors.New("invalid request type")
+    ErrItemNotFound      = errors.New("item not found")
+    ErrPermissionDenied  = errors.New("permission denied")
+)
+```
+
+### Shared Types (in `internal/types/`)
+```go
+package types
+
+import (
+    "time"
+    "github.com/google/uuid"
+    "github.com/uptrace/bun"
+)
+
+type Item struct {
+    bun.BaseModel `bun:"table:items,alias:i" swaggerignore:"true"`
+
+    ID          uuid.UUID  `bun:"id,pk,type:uuid" json:"id"`
+    Name        string     `bun:"name,notnull" json:"name"`
+    Description string     `bun:"description" json:"description,omitempty"`
+    UserID      uuid.UUID  `bun:"user_id,notnull,type:uuid" json:"user_id"`
+    CreatedAt   time.Time  `bun:"created_at,notnull,default:current_timestamp" json:"created_at"`
+    UpdatedAt   time.Time  `bun:"updated_at,notnull,default:current_timestamp" json:"updated_at"`
+    DeletedAt   *time.Time `bun:"deleted_at" json:"deleted_at,omitempty"`
+}
+```
+
+## Route Registration
+
+### Domain Routes File
+```go
+package routes
+
+import (
+    "github.com/go-fuego/fuego"
+    domainController "github.com/raghavyuva/nixopus-api/internal/features/[domain]/controller"
+)
+
+func (router *Router) RegisterDomainRoutes(
+    group *fuego.Server,
+    controller *domainController.DomainController,
+) {
+    fuego.Get(group, "", controller.ListItems)
+    fuego.Get(group, "/{id}", controller.GetItem)
+    fuego.Post(group, "", controller.CreateItem)
+    fuego.Put(group, "/{id}", controller.UpdateItem)
+    fuego.Delete(group, "/{id}", controller.DeleteItem)
+}
+```
+
+### Registering in Main Routes
+```go
+// In routes.go registerProtectedRoutes()
+domainController := domain.NewDomainController(
+    router.app.Store,
+    router.app.Ctx,
+    router.logger,
+    notificationManager,
+)
+domainGroup := fuego.Group(server, apiV1.Path+"/domain")
+router.applyMiddleware(domainGroup, MiddlewareConfig{
+    RBAC:         true,
+    FeatureFlag:  "domain",
+    Audit:        true,
+    ResourceName: "domain",
+})
+router.RegisterDomainRoutes(domainGroup, domainController)
+```
+
+## Error Handling
+
+### HTTP Error Responses
+```go
+// Use fuego.HTTPError for API errors
+return nil, fuego.HTTPError{
+    Err:    err,
+    Status: http.StatusBadRequest,
+}
+
+// For errors without underlying error
+return nil, fuego.HTTPError{
+    Err:    errors.New("custom error message"),
+    Status: http.StatusNotFound,
+}
+```
+
+### Logging Errors
+```go
+// Always log errors before returning
+c.logger.Log(logger.Error, err.Error(), additionalContext)
+return nil, fuego.HTTPError{Err: err, Status: http.StatusInternalServerError}
+```
+
+### Success Responses
+```go
+return &shared_types.Response{
+    Status:  "success",
+    Message: "Operation completed successfully",
+    Data:    result,
+}, nil
+```
+
+## Testing Patterns
+
+### Test Helper Functions
+```go
+// In internal/tests/helper.go
+func GetDomainURL() string {
+    return baseURL + "/domain"
+}
+
+func GetDomainItemURL(itemID string) string {
+    return baseURL + "/domain/" + itemID
+}
+```
+
+### Integration Tests
+```go
+package tests
+
+import (
+    "testing"
+    . "github.com/Eun/go-hit"
+)
+
+func TestCreateItem(t *testing.T) {
+    Test(t,
+        Description("Create item successfully"),
+        Post(GetDomainURL()),
+        Send().Headers("Content-Type").Add("application/json"),
+        Send().Headers("Authorization").Add("Bearer " + token),
+        Send().Headers("X-Organization-Id").Add(orgID),
+        Send().Body().JSON(map[string]interface{}{
+            "name": "Test Item",
+        }),
+        Expect().Status().Equal(200),
+        Expect().Body().JSON().JQ(".status").Equal("success"),
+    )
+}
+```
+
+## Middleware Usage
+
+### Available Middleware
+- `RBAC`: Role-based access control
+- `FeatureFlag`: Feature flag checking
+- `Audit`: Audit logging for operations
+
+### Applying Middleware
+```go
+router.applyMiddleware(group, MiddlewareConfig{
+    RBAC:         true,           // Enable RBAC checking
+    FeatureFlag:  "feature_name", // Feature flag to check (empty = disabled)
+    Audit:        true,           // Enable audit logging
+    ResourceName: "resource",     // Resource name for RBAC/audit
+})
+```
+
+## Code Quality
+
+### Comments — Minimal and Structured
+```go
+// ✅ Good: Function documentation
+// GetItems retrieves all items for a user with pagination.
+// Returns empty slice if no items found.
+func (s *DomainService) GetItems(userID string, page, pageSize int) ([]Item, int, error) {
+    // ...
+}
+
+// ✅ Good: Explain complex logic
+// Use transaction to ensure atomicity when updating multiple related records
+tx, err := s.DB.BeginTx(s.Ctx, nil)
+
+// ❌ Bad: Obvious comments
+// Get the user from context
+user := utils.GetUser(w, r)
+```
+
+### Clean Up Unused Code
+- Remove unused imports
+- Delete commented-out code
+- Remove unused variables and functions
+- Run `go mod tidy` to clean dependencies
+
+### Naming Conventions
+```go
+// Package names: lowercase, single word
+package controller
+
+// Interfaces: noun or noun phrase
+type DomainRepository interface {}
+
+// Structs: noun or noun phrase
+type DomainController struct {}
+type DomainService struct {}
+
+// Functions: verb or verb phrase
+func NewDomainController() *DomainController {}
+func (c *Controller) GetItems() {}
+func (s *Service) CreateItem() {}
+
+// Errors: Err prefix
+var ErrItemNotFound = errors.New("item not found")
+```
+
+## Quick Reference
+
+### Import Aliases
+```go
+import (
+    shared_storage "github.com/raghavyuva/nixopus-api/internal/storage"
+    shared_types "github.com/raghavyuva/nixopus-api/internal/types"
+    "github.com/raghavyuva/nixopus-api/internal/utils"
+    "github.com/raghavyuva/nixopus-api/internal/features/logger"
+)
+```
+
+### Common Utilities
+```go
+// Get authenticated user from context
+user := utils.GetUser(w, r)
+
+// Send error response (for non-fuego handlers)
+utils.SendErrorResponse(w, "error message", http.StatusBadRequest)
+
+// Send success response (for non-fuego handlers)
+utils.SendJSONResponse(w, "success", "message", data)
+
+// Logging
+c.logger.Log(logger.Error, "message", "additional context")
+c.logger.Log(logger.Info, "message", "")
+```
+
+### Checklist Before Committing
+- [ ] Early returns used (no deep nesting)
+- [ ] All errors logged before returning
+- [ ] Transaction used for mutations
+- [ ] Soft delete implemented (not hard delete)
+- [ ] Domain errors defined in types package
+- [ ] Repository interface defined for storage
+- [ ] Validation logic in validator package
+- [ ] Routes registered with appropriate middleware
+- [ ] Tests written for new endpoints
+- [ ] No unused imports or variables
+- [ ] `go fmt` and `go vet` pass
diff --git a/.cursor/rules/frontend.mdc b/.cursor/rules/frontend.mdc
@@ -0,0 +1,405 @@
+---
+description: TypeScript Next.js View Component Development Rules
+globs: view/**/*.{ts,tsx}
+alwaysApply: false
+---
+
+# Nixopus View Development Guidelines
+
+You are a senior frontend engineer building the Nixopus dashboard — a modern, visually rich Next.js application with TypeScript. Your focus is on crafting maintainable, performant, and beautiful user interfaces while maintaining strict code quality standards.
+
+## Core Principles
+
+### DRY (Don't Repeat Yourself) — Highest Priority
+- **Before writing any new logic**, search the codebase for existing implementations
+- Check `view/hooks/` for reusable hooks (e.g., `use-searchable`, `use-translation`, `use-mobile`)
+- Check `view/lib/utils.ts` for utility functions (e.g., `cn()`, `formatBytes()`, `formatDate()`)
+- Check `view/components/ui/` for shadcn components before creating custom elements
+- Reuse RTK Query hooks from `view/redux/services/` for data fetching
+- Extract repeated patterns into custom hooks or shared components
+
+### Single Responsibility Principle (SRP)
+- **Hooks**: Handle state management, side effects, and business logic
+- **Components**: Handle UI rendering and user interactions only
+- **Utils**: Pure functions for data transformation
+- **Services (RTK Query)**: API communication only
+- One hook/component should do one thing well
+
+### Code Readability
+```typescript
+// ✅ Good: Early returns, flat structure
+function useDeployment(id: string) {
+  const { data, isLoading, error } = useGetDeploymentQuery(id);
+  
+  if (!id) return { deployment: null, isReady: false };
+  if (isLoading) return { deployment: null, isReady: false };
+  if (error) return { deployment: null, isReady: false, error };
+  
+  return { deployment: data, isReady: true };
+}
+
+// ❌ Bad: Nested conditions
+function useDeployment(id: string) {
+  const { data, isLoading, error } = useGetDeploymentQuery(id);
+  
+  if (id) {
+    if (!isLoading) {
+      if (!error) {
+        return { deployment: data, isReady: true };
+      }
+    }
+  }
+  return { deployment: null, isReady: false };
+}
+```
+
+## Architecture
+
+### Directory Structure
+```
+view/
+├── app/                    # Next.js pages organized by domain
+│   └── [domain]/
+│       ├── components/     # Domain-specific components
+│       ├── hooks/          # Domain-specific hooks
+│       ├── utils/          # Domain-specific utilities
+│       └── page.tsx
+├── components/
+│   ├── ui/                 # shadcn base components (DO NOT MODIFY)
+│   └── [feature]/          # Shared feature components
+├── hooks/                  # Global reusable hooks
+├── lib/
+│   ├── i18n/              # Internationalization
+│   └── utils.ts           # Global utilities
+└── redux/
+    ├── services/          # RTK Query API definitions
+    ├── features/          # Redux slices
+    └── types/             # TypeScript interfaces
+```
+
+### Component Organization by Domain
+- Keep domain-related components in `app/[domain]/components/`
+- Shared components go in `components/[feature]/`
+- Break large components into smaller, focused chunks
+- Each component file should export one main component
+
+## State Management — RTK Query Always
+
+### Creating API Services
+```typescript
+// view/redux/services/[domain]/[domain]Api.ts
+import { createApi } from '@reduxjs/toolkit/query/react';
+import { baseQueryWithReauth } from '@/redux/base-query';
+import { ENDPOINTS } from '@/redux/api-conf';
+
+export const domainApi = createApi({
+  reducerPath: 'domainApi',
+  baseQuery: baseQueryWithReauth,
+  tagTypes: ['Domain'],
+  endpoints: (builder) => ({
+    getDomainItems: builder.query<DomainItem[], void>({
+      query: () => ({
+        url: ENDPOINTS.GET_DOMAIN_ITEMS,
+        method: 'GET'
+      }),
+      providesTags: [{ type: 'Domain', id: 'LIST' }],
+      transformResponse: (response: { data: DomainItem[] }) => response.data
+    }),
+    createDomainItem: builder.mutation<DomainItem, CreateDomainItemRequest>({
+      query: (data) => ({
+        url: ENDPOINTS.CREATE_DOMAIN_ITEM,
+        method: 'POST',
+        body: data
+      }),
+      invalidatesTags: [{ type: 'Domain', id: 'LIST' }]
+    })
+  })
+});
+
+export const { useGetDomainItemsQuery, useCreateDomainItemMutation } = domainApi;
+```
+
+### Using Redux Hooks
+```typescript
+// Always use typed hooks from @/redux/hooks
+import { useAppDispatch, useAppSelector } from '@/redux/hooks';
+
+// ✅ Correct
+const dispatch = useAppDispatch();
+const user = useAppSelector((state) => state.user);
+
+// ❌ Never use untyped versions
+import { useDispatch, useSelector } from 'react-redux';
+```
+
+## UI Components — shadcn Only
+
+### Always Use shadcn Components
+```typescript
+// ✅ Correct: Use shadcn components
+import { Button } from '@/components/ui/button';
+import { Card, CardHeader, CardContent } from '@/components/ui/card';
+import { Badge } from '@/components/ui/badge';
+import { Skeleton } from '@/components/ui/skeleton';
+
+// ❌ Never write plain HTML for interactive elements
+<button className="...">Click</button>
+<div className="card">...</div>
+```
+
+### Available shadcn Components
+Reference `view/components/ui/` for all available components:
+- Layout: `Card`, `Dialog`, `Sheet`, `Tabs`, `Collapsible`
+- Forms: `Button`, `Input`, `Select`, `Checkbox`, `Switch`, `Form`
+- Data: `Table`, `DataTable`, `Pagination`, `Badge`
+- Feedback: `Alert`, `Skeleton`, `Loading`, `Progress`
+- Navigation: `Breadcrumb`, `DropdownMenu`, `ContextMenu`
+
+### Styling with Tailwind
+```typescript
+// Use cn() utility for conditional classes
+import { cn } from '@/lib/utils';
+
+<Card className={cn(
+  "transition-all duration-300",
+  isActive && "border-primary",
+  isDisabled && "opacity-50 pointer-events-none"
+)} />
+```
+
+## TypeScript — Strict Typing
+
+### Never Use `any`
+```typescript
+// ✅ Correct: Explicit types
+interface DeploymentConfig {
+  name: string;
+  replicas: number;
+  environment: Record<string, string>;
+}
+
+function useDeployment(config: DeploymentConfig): DeploymentResult {
+  // ...
+}
+
+// ❌ Never use any
+function useDeployment(config: any): any {
+  // ...
+}
+```
+
+### Type Definitions Location
+- API response types: `view/redux/types/[domain].ts`
+- Component props: Inline or co-located with component
+- Shared types: Create in appropriate `types/` directory
+
+### Generic Patterns
+```typescript
+// Typed hook with generics
+function useSearchable<T>(
+  data: T[],
+  searchKeys: (keyof T)[],
+  defaultSort: SortConfig<T>
+): UseSearchableResult<T> {
+  // ...
+}
+```
+
+## Internationalization — No Hardcoded Strings
+
+### Always Use i18n
+```typescript
+import { useTranslation } from '@/hooks/use-translation';
+
+function MyComponent() {
+  const { t } = useTranslation();
+  
+  // ✅ Correct: Use translation keys
+  return (
+    <Button>{t('common.actions.save')}</Button>
+    <p>{t('dashboard.welcome.message', { name: userName })}</p>
+  );
+  
+  // ❌ Never hardcode user-facing text
+  return (
+    <Button>Save</Button>
+    <p>Welcome, {userName}!</p>
+  );
+}
+```
+
+### Translation File Structure
+```
+view/lib/i18n/locales/
+├── en/
+│   ├── common.json      # Shared strings (buttons, labels, errors)
+│   ├── dashboard.json   # Dashboard-specific strings
+│   ├── selfHost.json    # Self-host feature strings
+│   └── ...
+├── es/
+├── fr/
+└── ...
+```
+
+### Adding New Translations
+1. Add key to English locale first: `view/lib/i18n/locales/en/[domain].json`
+2. Use descriptive, hierarchical keys: `domain.section.element`
+3. Support parameters: `"greeting": "Hello, {name}!"`
+
+## Code Quality
+
+### Clean Up Unused Code
+- Remove unused imports immediately
+- Delete commented-out code
+- Remove unused variables and functions
+- Keep files focused and minimal
+
+### Comments — Minimal and Structured
+```typescript
+// ✅ Good: JSDoc for complex hooks/functions
+/**
+ * Manages pagination state for GitHub repositories with server-side filtering.
+ * Resets page on search/filter changes.
+ */
+function useGithubRepoPagination() {
+  // ...
+}
+
+// ✅ Good: Explain WHY, not WHAT
+// Reset page when filters change to avoid showing empty results
+useEffect(() => {
+  setCurrentPage(1);
+}, [searchTerm, sortConfig]);
+
+// ❌ Bad: Obvious comments
+// Set the current page to 1
+setCurrentPage(1);
+
+// ❌ Bad: Commented code
+// const oldImplementation = () => { ... }
+```
+
+### Linting & Formatting
+- Respect ESLint rules configured in `view/eslint.config.mjs`
+- Use Prettier for consistent formatting
+- Fix all lint errors before committing
+- Never disable lint rules without strong justification
+
+## Component Patterns
+
+### Hook-Component Separation
+```typescript
+// hooks/use-deployment-form.ts
+export function useDeploymentForm(initialValues: DeploymentFormValues) {
+  const [createDeployment, { isLoading }] = useCreateDeploymentMutation();
+  const { t } = useTranslation();
+  
+  const handleSubmit = async (values: DeploymentFormValues) => {
+    try {
+      await createDeployment(values).unwrap();
+      toast.success(t('toasts.deployment.created'));
+    } catch (error) {
+      toast.error(t('toasts.deployment.error'));
+    }
+  };
+  
+  return { handleSubmit, isLoading };
+}
+
+// components/deployment-form.tsx
+export function DeploymentForm({ initialValues }: DeploymentFormProps) {
+  const { handleSubmit, isLoading } = useDeploymentForm(initialValues);
+  const { t } = useTranslation();
+  
+  return (
+    <Form onSubmit={handleSubmit}>
+      <FormInputField name="name" label={t('selfHost.form.name')} />
+      <Button type="submit" disabled={isLoading}>
+        {t('common.actions.deploy')}
+      </Button>
+    </Form>
+  );
+}
+```
+
+### Loading & Error States
+```typescript
+function RepositoryList() {
+  const { data, isLoading, error } = useGetRepositoriesQuery();
+  const { t } = useTranslation();
+  
+  if (isLoading) return <RepositoryListSkeleton />;
+  if (error) return <ErrorHandler message={t('errors.loadFailed')} />;
+  if (!data?.length) return <EmptyState message={t('selfHost.empty')} />;
+  
+  return (
+    <div className="grid gap-4">
+      {data.map((repo) => (
+        <RepositoryCard key={repo.id} {...repo} />
+      ))}
+    </div>
+  );
+}
+```
+
+### Skeleton Loaders
+Always provide skeleton loaders for async content:
+```typescript
+export const RepositoryCardSkeleton: React.FC = () => (
+  <Card>
+    <CardHeader>
+      <Skeleton className="h-6 w-40" />
+      <Skeleton className="h-4 w-full mt-2" />
+    </CardHeader>
+    <CardContent>
+      <Skeleton className="h-4 w-24" />
+    </CardContent>
+  </Card>
+);
+```
+
+## UX Best Practices
+
+### User Experience First
+- Provide immediate feedback for all actions (loading states, toasts)
+- Use optimistic updates where appropriate
+- Handle error states gracefully with recovery options
+- Maintain consistent navigation patterns
+- Ensure responsive design works on all screen sizes
+
+### Accessibility
+- Use semantic HTML elements
+- Provide proper ARIA labels where needed
+- Ensure keyboard navigation works
+- Maintain sufficient color contrast
+
+### Performance
+- Memoize expensive computations with `useMemo`
+- Prevent unnecessary re-renders with `useCallback`
+- Use React Query's caching effectively
+- Lazy load heavy components when appropriate
+
+## Quick Reference
+
+### Import Aliases
+```typescript
+import { ... } from '@/components/ui/...'    // shadcn components
+import { ... } from '@/hooks/...'            // Global hooks
+import { ... } from '@/redux/hooks'          // useAppDispatch, useAppSelector
+import { ... } from '@/redux/services/...'   // RTK Query hooks
+import { ... } from '@/redux/types/...'      // Type definitions
+import { ... } from '@/lib/utils'            // Utility functions
+import { ... } from '@/lib/i18n/...'         // i18n config
+```
+
+### Checklist Before Committing
+- [ ] No `any` types
+- [ ] No hardcoded strings (using i18n)
+- [ ] Using shadcn components (no plain HTML buttons, inputs, etc.)
+- [ ] Logic in hooks, UI in components
+- [ ] No nested if statements (use early returns)
+- [ ] Removed unused imports and variables
+- [ ] Loading and error states handled
+- [ ] Types properly defined
+- [ ] Linter passes with no errors
+f
\ No newline at end of file
diff --git a/.cursor/rules/installer_cli.mdc b/.cursor/rules/installer_cli.mdc
@@ -0,0 +1,582 @@
+---
+description: Python CLI Development Rules for Nixopus CLI
+globs: cli/**/*.py
+alwaysApply: false
+---
+
+# Nixopus CLI Development Guidelines
+
+You are a senior Python engineer building the Nixopus CLI — a production-grade command-line tool using Typer, Rich, and Pydantic. Your focus is on writing clean, maintainable, and user-friendly CLI commands following established patterns.
+
+## Core Principles
+
+### DRY (Don't Repeat Yourself) — Highest Priority
+- **Before writing new code**, search the codebase for existing implementations
+- Check `app/utils/` for shared utilities (`logger`, `config`, `output_formatter`, `timeout`)
+- Check `app/utils/protocols.py` for protocol definitions
+- Reuse existing message patterns from `messages.py` files
+- Extract common validation logic to shared validators
+
+### Single Responsibility Principle (SRP)
+- **Commands**: CLI interface and argument parsing only
+- **Run/Logic files**: Business logic and orchestration
+- **Messages**: User-facing strings (separated from logic)
+- **Types**: Data classes and type definitions
+- **Utils**: Reusable utility functions
+- Each file should have one primary purpose
+
+### Code Readability
+```python
+# ✅ Good: Early returns, flat structure
+def clone_repository(repo: str, path: str, logger: LoggerProtocol) -> tuple[bool, Optional[str]]:
+    if not repo:
+        return False, "Repository URL is required"
+    
+    if not validate_repo_url(repo):
+        return False, "Invalid repository URL"
+    
+    try:
+        result = git_clone(repo, path)
+        return True, None
+    except Exception as e:
+        return False, str(e)
+
+# ❌ Bad: Nested conditions
+def clone_repository(repo: str, path: str, logger: LoggerProtocol) -> tuple[bool, Optional[str]]:
+    if repo:
+        if validate_repo_url(repo):
+            try:
+                result = git_clone(repo, path)
+                return True, None
+            except Exception as e:
+                return False, str(e)
+        else:
+            return False, "Invalid repository URL"
+    else:
+        return False, "Repository URL is required"
+```
+
+## Architecture
+
+### Directory Structure
+```
+cli/
+├── app/
+│   ├── __init__.py
+│   ├── main.py                 # Entry point, Typer app registration
+│   ├── commands/               # Command modules
+│   │   └── [command]/
+│   │       ├── __init__.py
+│   │       ├── command.py      # Typer command definitions
+│   │       ├── messages.py     # User-facing strings
+│   │       ├── types.py        # Dataclasses & types
+│   │       └── [logic].py      # Business logic
+│   └── utils/                  # Shared utilities
+│       ├── __init__.py
+│       ├── config.py           # Configuration loading
+│       ├── logger.py           # Logging utilities
+│       ├── message.py          # Global messages
+│       ├── output_formatter.py # Output formatting
+│       ├── protocols.py        # Protocol definitions
+│       └── timeout.py          # Timeout utilities
+├── pyproject.toml              # Poetry configuration
+└── tests/                      # Test files
+```
+
+### Creating a New Command
+
+1. Create the directory structure:
+```
+app/commands/[command]/
+├── __init__.py
+├── command.py      # or [command].py
+├── messages.py
+└── types.py        # if needed
+```
+
+2. Register in `app/main.py`:
+```python
+from app.commands.[command].command import [command]_app
+
+app.add_typer([command]_app, name="[command]")
+```
+
+## Typer Command Patterns
+
+### Command File Structure
+```python
+from typing import Optional
+import typer
+from app.utils.logger import create_logger, log_error, log_success
+from app.utils.timeout import timeout_wrapper
+from .messages import operation_failed, operation_success
+from .types import CommandParams
+
+command_app = typer.Typer(help="Command description", invoke_without_command=True)
+
+
+@command_app.callback()
+def command_callback(
+    ctx: typer.Context,
+    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show more details"),
+    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout in seconds"),
+    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Preview changes without executing"),
+    force: bool = typer.Option(False, "--force", "-f", help="Force operation"),
+):
+    """Main command description"""
+    if ctx.invoked_subcommand is None:
+        logger = create_logger(verbose=verbose)
+        params = CommandParams(
+            logger=logger,
+            verbose=verbose,
+            timeout=timeout,
+            dry_run=dry_run,
+            force=force,
+        )
+        run_command(params)
+
+
+@command_app.command(name="subcommand")
+def subcommand(
+    arg: str = typer.Argument(..., help="Required argument"),
+    option: str = typer.Option(None, "--option", "-o", help="Optional argument"),
+    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
+):
+    """Subcommand description"""
+    logger = create_logger(verbose=verbose)
+    try:
+        with timeout_wrapper(timeout):
+            result = execute_subcommand(arg, option)
+        log_success(operation_success, verbose=verbose)
+    except TimeoutError as e:
+        log_error(str(e), verbose=verbose)
+        raise typer.Exit(1)
+    except Exception as e:
+        log_error(str(e), verbose=verbose)
+        raise typer.Exit(1)
+```
+
+### Standard CLI Options
+```python
+# Always include these common options where applicable
+verbose: bool = typer.Option(False, "--verbose", "-v", help="Show more details")
+timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout in seconds")
+dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Preview without executing")
+force: bool = typer.Option(False, "--force", "-f", help="Force operation")
+output: str = typer.Option("text", "--output", "-o", help="Output format (text, json)")
+```
+
+## Messages Pattern
+
+### Messages File Structure
+```python
+# app/commands/[command]/messages.py
+
+# Operation messages
+operation_starting = "Starting operation..."
+operation_success = "Operation completed successfully"
+operation_failed = "Operation failed"
+operation_timed_out = "Operation timed out after {timeout} seconds"
+
+# Validation messages
+missing_required_field = "{field} is required"
+invalid_format = "Invalid {field} format: {value}"
+
+# Step messages
+step_starting = "Starting {step_name}..."
+step_completed = "{step_name} completed"
+step_failed = "{step_name} failed: {error}"
+
+# Dry run messages
+dry_run_mode = "=== DRY RUN MODE ==="
+dry_run_would_execute = "[DRY RUN] Would execute: {action}"
+end_dry_run = "=== END DRY RUN ==="
+
+# Debug messages (prefix with debug_)
+debug_config_loaded = "DEBUG: Configuration loaded from {path}"
+debug_step_execution = "DEBUG: Executing step: {step}"
+```
+
+### Using Messages
+```python
+from .messages import operation_success, operation_failed, step_failed
+
+# ✅ Good: Use message templates with format()
+logger.error(step_failed.format(step_name="Clone", error=str(e)))
+
+# ❌ Bad: Hardcode strings in logic
+logger.error(f"Clone failed: {str(e)}")
+```
+
+## Types Pattern
+
+### Dataclass for Parameters
+```python
+# app/commands/[command]/types.py
+from dataclasses import dataclass
+from typing import Optional
+from app.utils.protocols import LoggerProtocol
+
+
+@dataclass
+class CommandParams:
+    logger: Optional[LoggerProtocol] = None
+    verbose: bool = False
+    timeout: int = 300
+    force: bool = False
+    dry_run: bool = False
+    # Add command-specific fields
+    target: Optional[str] = None
+    config_file: Optional[str] = None
+```
+
+### Pydantic Models for Output
+```python
+from typing import Any, Dict, Optional
+from pydantic import BaseModel
+
+
+class OperationResult(BaseModel):
+    success: bool
+    message: str
+    data: Optional[Dict[str, Any]] = None
+    error: Optional[str] = None
+```
+
+## Return Patterns
+
+### Tuple Returns for Operations
+```python
+# ✅ Standard pattern: Return (success: bool, error: Optional[str])
+def execute_step(params: CommandParams) -> tuple[bool, Optional[str]]:
+    if params.dry_run:
+        if params.logger:
+            params.logger.info(dry_run_would_execute.format(action="step"))
+        return True, None
+    
+    try:
+        # Execute operation
+        return True, None
+    except Exception as e:
+        return False, str(e)
+
+
+# Usage
+success, error = execute_step(params)
+if not success:
+    logger.error(step_failed.format(step_name="Step", error=error))
+    raise typer.Exit(1)
+```
+
+### Step-Based Execution
+```python
+from typing import Callable, List, Tuple
+from rich.progress import Progress, SpinnerColumn, TextColumn
+
+
+def build_steps(params: CommandParams) -> List[Tuple[str, Callable[[], tuple[bool, Optional[str]]]]]:
+    """Build list of steps to execute"""
+    return [
+        ("Validating input", lambda: validate_input(params)),
+        ("Executing operation", lambda: execute_operation(params)),
+        ("Cleaning up", lambda: cleanup(params)),
+    ]
+
+
+def run_with_progress(steps: List[Tuple[str, Callable]], params: CommandParams) -> None:
+    """Execute steps with progress indicator"""
+    with Progress(
+        SpinnerColumn(),
+        TextColumn("[progress.description]{task.description}"),
+        transient=True,
+    ) as progress:
+        task = progress.add_task("Processing...", total=len(steps))
+        
+        for step_name, step_func in steps:
+            progress.update(task, description=step_name)
+            success, error = step_func()
+            if not success:
+                raise Exception(step_failed.format(step_name=step_name, error=error))
+            progress.advance(task)
+```
+
+## Logging Patterns
+
+### Using the Logger
+```python
+from app.utils.logger import create_logger, log_error, log_success, log_info
+
+
+# Create logger with verbosity
+logger = create_logger(verbose=verbose)
+
+# Use logger methods
+logger.info("Information message")
+logger.debug("Debug message (only shown with --verbose)")
+logger.warning("Warning message")
+logger.error("Error message")
+logger.success("Success message")
+logger.highlight("Highlighted message")
+
+# Or use standalone functions
+log_info("Info", verbose=verbose)
+log_error("Error", verbose=verbose)
+log_success("Success", verbose=verbose)
+```
+
+### Logger Protocol
+```python
+# Always type hint with LoggerProtocol for flexibility
+from app.utils.protocols import LoggerProtocol
+
+
+def execute_operation(
+    params: OperationParams,
+    logger: Optional[LoggerProtocol] = None,
+) -> tuple[bool, Optional[str]]:
+    if logger:
+        logger.info(operation_starting)
+    # ...
+```
+
+## Configuration Patterns
+
+### Loading Configuration
+```python
+from app.utils.config import (
+    get_active_config,
+    get_config_value,
+    get_config_file_path,
+)
+
+# Load config (user config or default)
+config = get_active_config(user_config_file=params.config_file)
+
+# Get value using dot notation
+repo_url = get_config_value(config, "clone.repo")
+api_port = get_config_value(config, "services.api.env.PORT")
+```
+
+### Config Path Constants
+```python
+# Define constants for commonly used config paths
+# In app/utils/config.py
+DEFAULT_REPO = "clone.repo"
+DEFAULT_BRANCH = "clone.branch"
+API_PORT = "services.api.env.PORT"
+VIEW_PORT = "services.view.env.NEXT_PUBLIC_PORT"
+```
+
+## Output Formatting
+
+### Text and JSON Output
+```python
+from app.utils.output_formatter import (
+    format_output,
+    create_success_message,
+    create_error_message,
+    create_table,
+)
+
+
+def format_result(result: Any, output_format: str) -> str:
+    if output_format == "json":
+        return format_output(result, "json")
+    return format_output(result, "text")
+
+
+# Create structured output
+result = create_success_message(
+    message="Operation completed",
+    data={"items": 5, "status": "healthy"}
+)
+
+# Create table output
+table = create_table(
+    data={"Key1": "Value1", "Key2": "Value2"},
+    title="Results",
+    headers=("Property", "Value"),
+)
+```
+
+## Error Handling
+
+### Graceful Exit Pattern
+```python
+import typer
+
+
+def run_command(params: CommandParams) -> None:
+    try:
+        success, error = execute_operation(params)
+        if not success:
+            if params.logger:
+                params.logger.error(operation_failed.format(error=error))
+            raise typer.Exit(1)
+        
+        if params.logger:
+            params.logger.success(operation_success)
+            
+    except TimeoutError:
+        if params.logger:
+            params.logger.error(operation_timed_out.format(timeout=params.timeout))
+        raise typer.Exit(1)
+    except Exception as e:
+        if params.logger:
+            params.logger.error(f"{operation_failed}: {str(e)}")
+        raise typer.Exit(1)
+```
+
+### Timeout Wrapper
+```python
+from app.utils.timeout import timeout_wrapper
+
+
+try:
+    with timeout_wrapper(params.timeout):
+        result = long_running_operation()
+except TimeoutError:
+    logger.error(operation_timed_out.format(timeout=params.timeout))
+    raise typer.Exit(1)
+```
+
+## Dry Run Pattern
+
+### Implementing Dry Run
+```python
+def execute_operation(params: CommandParams) -> tuple[bool, Optional[str]]:
+    if params.dry_run:
+        if params.logger:
+            params.logger.info(dry_run_mode)
+            params.logger.info(dry_run_would_execute.format(action="operation"))
+            params.logger.info(end_dry_run)
+        return True, None
+    
+    # Actual implementation
+    try:
+        # Execute real operation
+        return True, None
+    except Exception as e:
+        return False, str(e)
+```
+
+## Code Quality
+
+### Type Hints — Always Use
+```python
+from typing import Any, Callable, Dict, List, Optional, Tuple
+
+
+# ✅ Good: Full type hints
+def process_items(
+    items: List[Dict[str, Any]],
+    filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
+) -> Tuple[List[Dict[str, Any]], int]:
+    ...
+
+
+# ❌ Bad: No type hints
+def process_items(items, filter_fn=None):
+    ...
+```
+
+### Comments — Minimal and Structured
+```python
+# ✅ Good: Docstring for public functions
+def clone_repository(
+    repo: str,
+    path: str,
+    branch: str,
+    logger: Optional[LoggerProtocol] = None,
+) -> tuple[bool, Optional[str]]:
+    """Clone a git repository to the specified path.
+    
+    Args:
+        repo: Repository URL to clone
+        path: Local path to clone to
+        branch: Branch to checkout
+        logger: Optional logger for output
+        
+    Returns:
+        Tuple of (success, error_message)
+    """
+    ...
+
+
+# ✅ Good: Explain complex logic
+# Use innermost placeholder first to support nested expansions
+match = find_innermost_placeholder(value)
+
+# ❌ Bad: Obvious comments
+# Clone the repository
+clone_repository(repo, path)
+```
+
+### Clean Up Unused Code
+- Remove unused imports
+- Delete commented-out code
+- Remove unused variables and functions
+- Run `black` and `isort` before committing
+
+## Testing Patterns
+
+### Test Structure
+```python
+# tests/test_[command].py
+import pytest
+from app.commands.[command].command import execute_operation
+from app.commands.[command].types import CommandParams
+
+
+class TestCommand:
+    def test_successful_operation(self):
+        params = CommandParams(dry_run=True)
+        success, error = execute_operation(params)
+        assert success is True
+        assert error is None
+
+    def test_failed_operation(self):
+        params = CommandParams(timeout=0)
+        success, error = execute_operation(params)
+        assert success is False
+        assert error is not None
+```
+
+## Quick Reference
+
+### Import Patterns
+```python
+# Standard library
+from dataclasses import dataclass
+from pathlib import Path
+from typing import Any, Callable, Dict, List, Optional, Tuple
+
+# Third party
+import typer
+from pydantic import BaseModel
+from rich.console import Console
+from rich.progress import Progress
+
+# Local - utils
+from app.utils.config import get_active_config, get_config_value
+from app.utils.logger import create_logger, log_error, log_success
+from app.utils.output_formatter import format_output, create_table
+from app.utils.protocols import LoggerProtocol
+from app.utils.timeout import timeout_wrapper
+
+# Local - relative imports within command
+from .messages import operation_success, operation_failed
+from .types import CommandParams
+```
+
+### Checklist Before Committing
+- [ ] Type hints on all functions
+- [ ] User-facing strings in messages.py
+- [ ] Dry run support implemented
+- [ ] Timeout wrapper for long operations
+- [ ] Proper error handling with typer.Exit
+- [ ] Logger used consistently
+- [ ] Return pattern: `tuple[bool, Optional[str]]`
+- [ ] No hardcoded strings in logic
+- [ ] Black and isort formatting applied
+- [ ] Tests written for new functionality
PATCH

echo "Gold patch applied."
