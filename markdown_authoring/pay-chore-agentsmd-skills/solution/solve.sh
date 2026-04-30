#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pay

# Idempotency guard
if grep -qF "description: \"Use when local PHP environment is unavailable. Fallback container-" ".agents/skills/container-dev/SKILL.md" && grep -qF "| \u652f\u4ed8\u5b9d | \u65e0 | `FormatPayloadBizContentPlugin` \u2192 `AddPayloadSignaturePlugin` \u2192 `Add" ".agents/skills/pr-review-provider/SKILL.md" && grep -qF "| URL \u6784\u5efa | `AlipayTrait::getAlipayUrl()`\u3001`WechatTrait::getWechatUrl()`\u3001`UnipayTr" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/container-dev/SKILL.md b/.agents/skills/container-dev/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: container-dev
-description: "Use this when local PHP environment is unavailable. Fallback container-based development environment for yansongda/pay project."
+description: "Use when local PHP environment is unavailable. Fallback container-based development environment for yansongda/pay project."
 ---
 
 # Container-based Local Development (Fallback)
@@ -11,100 +11,143 @@ description: "Use this when local PHP environment is unavailable. Fallback conta
 
 **优先本地环境**：先检查本地是否有 PHP/composer，有则直接使用。
 
-**容器作为备选**：仅在本地环境不可用时使用容器（Apple Container 或 Docker）。
+**容器作为备选**：仅在本地环境不可用时使用容器。
 
-## 镜像
+## 快速参考
+
+### 镜像
 
 ```
 registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine
 ```
 
-## Apple Container 命令
+### 常用命令
+
+| 任务 | 命令 |
+|------|------|
+| 运行测试 | `composer test` |
+| PHPStan 分析 | `composer analyse` |
+| 代码风格检查 | `composer cs-fix`（**仅检查，不修复**） |
+| 代码风格修复 | `php-cs-fixer fix ./src` |
+| Composer 更新 | `composer update --with-all-dependencies` |
+| 安装依赖 | `composer install` |
+| Web 文档开发 | `pnpm web:dev`（需本地 Node 或 Node 容器） |
+| Web 文档构建 | `pnpm web:build`（需本地 Node 或 Node 容器） |
+
+---
+
+## Apple Container
 
-### 正常情况（网络正常）
+### 基本模板
 
 ```bash
 container run --rm -v "$(pwd)":/app -w /app \
   registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
-  YOUR_COMMAND
+  COMMAND
 ```
 
-### 网络异常时（DNS 问题）
+### DNS 问题处理
 
-如果 container 网络出现 DNS 解析失败（如 `198.18.0.x` 地址、连接超时），添加 DNS 配置：
+若出现 DNS 解析失败（`198.18.0.x` 地址、连接超时），添加 DNS fix：
 
 ```bash
 container run --rm -v "$(pwd)":/app -w /app \
   registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
-  sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf && YOUR_COMMAND"
+  sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf && COMMAND"
 ```
 
-### 常用命令示例
+### PHP 命令示例
 
 ```bash
-# 运行测试
+# 测试（需 DNS fix + COMPOSER_ALLOW_SUPERUSER）
 container run --rm -v "$(pwd)":/app -w /app \
   registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
   sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf && COMPOSER_ALLOW_SUPERUSER=1 composer test"
 
-# Composer update
-container run --rm -v "$(pwd)":/app -w /app \
-  registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
-  sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf && composer update --with-all-dependencies"
-
 # PHPStan 分析
 container run --rm -v "$(pwd)":/app -w /app \
   registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
   sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf && COMPOSER_ALLOW_SUPERUSER=1 composer analyse"
 
-# CS-Fixer
+# 代码风格检查（仅查看差异）
 container run --rm -v "$(pwd)":/app -w /app \
   registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
   sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf && COMPOSER_ALLOW_SUPERUSER=1 composer cs-fix"
+
+# 代码风格修复
+container run --rm -v "$(pwd)":/app -w /app \
+  registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
+  sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf && COMPOSER_ALLOW_SUPERUSER=1 php-cs-fixer fix ./src"
+
+# Composer update
+container run --rm -v "$(pwd)":/app -w /app \
+  registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
+  sh -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf && composer update --with-all-dependencies"
 ```
 
-## Docker 命令
+### Web 文档命令
+
+Web 文档使用 pnpm，镜像中无 Node.js，需使用 Node 镜像或本地运行。
 
-Docker 命令与 Apple Container 类似，只需将 `container` 替换为 `docker`：
+**注意**：`web/package.json` 要求 Node `>=20.12.0`，请确保使用的镜像版本满足此约束。
 
 ```bash
-# 运行测试
-docker run --rm -v "$(pwd)":/app -w /app \
-  registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
-  composer test
+# 方案1: 本地运行（推荐）
+cd web && pnpm web:dev
 
-# Composer update
+# 方案2: 使用 Node 容器（版本 >=20.12.0）
+docker run --rm -v "$(pwd)/web":/app -w /app \
+  node:20-alpine \
+  sh -c "npm install -g pnpm && pnpm install && pnpm web:dev"
+```
+
+---
+
+## Docker
+
+Docker 命令类似，通常不需要 DNS fix：
+
+```bash
+# 测试
 docker run --rm -v "$(pwd)":/app -w /app \
   registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
-  composer update --with-all-dependencies
+  composer test
 
 # PHPStan 分析
 docker run --rm -v "$(pwd)":/app -w /app \
   registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
   composer analyse
 
-# CS-Fixer
+# 代码风格检查
 docker run --rm -v "$(pwd)":/app -w /app \
   registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
   composer cs-fix
+
+# 代码风格修复
+docker run --rm -v "$(pwd)":/app -w /app \
+  registry.cn-shenzhen.aliyuncs.com/yansongda/php:cli-8.3-alpine \
+  php-cs-fixer fix ./src
 ```
 
-**注意**：Docker 通常不需要 DNS fix，网络配置更稳定。
+---
 
 ## DNS 问题诊断（Apple Container）
 
 **症状**：
 - `curl error 28 Connection timed out`
 - DNS 解析返回 `198.18.0.x`（基准测试保留地址）
-- `nslookup` 显示 Server 为 `192.168.64.1:53`
 
-**原因**：Container 系统 DNS 解析器异常，无法正确解析公网域名。
+**原因**：Container 系统 DNS 解析器异常。
 
 **解决**：手动写入 `nameserver 8.8.8.8` 到 `/etc/resolv.conf`。
 
+---
+
 ## 注意事项
 
-- 使用 `COMPOSER_ALLOW_SUPERUSER=1` 运行 composer 脚本命令
-- 容器内网络可能无法访问某些 CDN，测试中可能出现 PHP warning，不影响核心功能
-- Apple Container 需先启动系统服务：`container system start`
-- Docker 需确保 Docker Desktop 或 Docker daemon 已启动
\ No newline at end of file
+- `COMPOSER_ALLOW_SUPERUSER=1`：容器内运行 composer 脚本必须
+- `composer cs-fix`：**仅检查并显示差异**，不自动修复
+- `php-cs-fixer fix ./src`：实际修复代码风格
+- Apple Container 需先启动：`container system start`
+- Docker 需确保 Docker Desktop 或 daemon 已启动
+- 容器内网络可能无法访问某些 CDN，测试中可能出现 PHP warning（不影响核心功能）
\ No newline at end of file
diff --git a/.agents/skills/pr-review-provider/SKILL.md b/.agents/skills/pr-review-provider/SKILL.md
@@ -7,20 +7,75 @@ description: "Use when reviewing PRs that add or modify a payment Provider in ya
 
 yansongda/pay 新增/修改 Provider 时的 Code Review 专用检查清单。基于 Airwallex PR #1140 review 经验沉淀。
 
-## 核心架构速查
+## Review 流程
 
-```
-StartPlugin → ObtainTokenPlugin → 业务插件 → AddPayloadBodyPlugin → AddRadarPlugin → ResponsePlugin → ParserPlugin
-```
+按以下阶段顺序审查，确保覆盖完整：
+
+1. **Phase 1**: Provider 结构完整性
+2. **Phase 2**: 代码规范检查
+3. **Phase 3**: 安全性检查（签名验证、加密解密）
+4. **Phase 4**: 架构一致性（管道、Trait、Event）
+5. **Phase 5**: 官方文档对照
+6. **Phase 6**: 测试覆盖
+7. **Phase 7**: 文档完整性
+
+---
+
+## Phase 1: Provider 结构完整性
+
+对照以下清单逐项检查：
+
+| # | 检查项 | 位置 | 说明 |
+|---|--------|------|------|
+| 1 | 插件 | `src/Plugin/{Provider}/V{n}/` | 按版本组织 |
+| 2 | Provider 类 | `src/Provider/{Provider}.php` | 实现 `ProviderInterface` |
+| 3 | 服务提供者 | `src/Service/{Provider}ServiceProvider.php` | 服务注册 |
+| 4 | 快捷方式 | `src/Shortcut/{Provider}/` | `{Method}Shortcut.php` |
+| 5 | Trait 方法 | `src/Traits/{Provider}Trait.php` | `get{Provider}Url`、`verify{Provider}WebhookSign` 等 |
+| 6 | Provider 注册 | `src/Pay.php` | 添加 `{Provider}::class` 和入口方法 |
+| 7 | 异常常量 | `src/Exception/Exception.php` | `PARAMS_{PROVIDER}_*`、`CONFIG_{PROVIDER}_*` |
+| 8 | 测试 | `tests/` | 与源码结构对应 |
+| 9 | 文档 | `web/docs/v3/{provider}/` | VitePress 文档 |
+| 10 | 侧边栏/CHANGELOG | `web/.vitepress/sidebar/v3.js`、`CHANGELOG.md` | 更新配置 |
+
+**注意**：`src/Functions.php` 已不存在，URL/签名等方法已下沉到 `src/Traits/*Trait.php`。
+
+---
+
+## Phase 2: 代码规范检查
+
+### 基本规范
+
+| 检查项 | 要求 |
+|--------|------|
+| `declare(strict_types=1)` | 每个文件必须有 |
+| `use` 导入 | 除动态类名字符串/反射场景外，禁止直接写完整命名空间（如 `\Yansongda\Pay\...`） |
+| 多行条件 | `&&` / `||` 放在续行开头 |
 
-- `Rocket` 承载 params（用户入参，含 `_config`）、payload（API 请求体）、radar（HTTP 请求）、destination（响应）
-- `params` 和 `payload` 是两个不同概念，**绝对不能混淆**
+### 命名规范
 
-## 必查项（Bug 高发区）
+| 类型 | 格式 | 示例 |
+|------|------|------|
+| 插件 | `{Action}Plugin.php` | `PayPlugin`、`RefundPlugin` |
+| 快捷方式 | `{Method}Shortcut.php` | `WebShortcut`、`QueryShortcut` |
+| Provider | `{ProviderName}.php` | `Paypal.php`、`Stripe.php` |
+| ServiceProvider | `{ProviderName}ServiceProvider.php` | `PaypalServiceProvider.php` |
+| Trait | `{Provider}Trait.php` | `WechatTrait`、`StripeTrait` |
+| 命名空间 | `Yansongda\Pay\Plugin\{Provider}\V{n}\Pay\{Plugin}` | 版本号与 API 版本一致 |
+
+### 日志与异常
+
+- 日志格式：`[Provider][V{n}][Category][Plugin]`，使用中文消息
+- 异常常量：`PARAMS_{PROVIDER}_*`、`CONFIG_{PROVIDER}_*`
+- 异常消息：中文，附带上下文参数
+
+---
+
+## Phase 3: 安全性检查
 
 ### 1. params vs payload 混淆
 
-**高危**：任何调用 `Artful::artful($plugins, $xxx)` 的地方，第二参数必须是 `params`（含 `_config`），不能是 `payload`。
+**高危**：`Artful::artful()` 第二参数必须是 `params`（含 `_config`），不能是 `payload`。
 
 ```php
 // ❌ 错误 — payload 不含 _config，多租户必崩
@@ -30,132 +85,240 @@ $result = Artful::artful([...], $confirmPayload);
 $result = Artful::artful([...], $confirmParams);
 ```
 
-**检查方法**：搜索所有 `Artful::artful(` 调用，追踪第二参数来源是 `getParams()` 还是 `getPayload()`。
+**检查方法**：搜索 `Artful::artful(` 调用，追踪第二参数来源。
+
+### 2. 空值处理
 
-### 2. 可选字段缺少 array_filter
+检查最终发送的 body/query 是否包含不应出现的 `null`/空字段。
 
-**中高危**：`mergePayload` 中的可选字段必须用 `array_filter` 包裹，否则 `null` 值会被发送到支付 API。
+**推荐方式**：
+- 优先使用 `filter_params()` 函数（artful 库提供）
+- 嵌套数组场景补充 `array_filter()`
 
 ```php
-// ❌ null 值会被序列化发送
-$rocket->mergePayload([
-    'optional_field' => $payload->get('optional_field'),
-]);
+// ✅ 优先方式 — filter_params
+$body = http_build_query(filter_params($payload)->toArray());
 
-// ✅ 正确
+// ✅ 嵌套场景 — array_filter
 $rocket->mergePayload(array_filter([
-    'optional_field' => $payload->get('optional_field'),
+    'application_context' => $payload->get('application_context'),
 ], static fn ($value) => !is_null($value)));
 ```
 
-**检查方法**：逐个对比所有业务 Plugin 的 `mergePayload` 调用，确认一致性。
+**检查位置**：`AddRadarPlugin::getBody()`、`getQueryString()`、业务 Plugin 的 `mergePayload()`。
 
 ### 3. Webhook 签名验证
 
-**安全强制**：所有回调必须验签。
+**安全强制**：所有 CallbackPlugin 必须验签。
 
-| 检查点 | 要求 |
-|--------|------|
-| `CallbackPlugin` 调用了签名验证 | 必须 |
-| 签名算法与官方文档一致 | 必须对照 @see 链接验证 |
-| `webhook_secret` 缺失时抛异常 | 必须 |
-| 签名为空时抛异常 | 必须 |
-| 使用 `hash_equals` 防时序攻击 | 必须 |
+| Provider | Trait 方法 | 必需配置字段 |
+|----------|------------|--------------|
+| Stripe | `StripeTrait::verifyStripeWebhookSign()` | `webhook_secret` |
+| PayPal | `PaypalTrait::verifyPaypalWebhookSign()` | `webhook_id` + OAuth |
+| 微信 | `WechatTrait::verifyWechatSign()` | `mch_secret_cert`、`wechat_public_cert_path`（可预置或运行时拉取） |
+| 抖音 | —（在 `CallbackPlugin::verifySign()` 中实现） | `mch_secret_token`、`mch_secret_salt` |
+| 银联 | `UnipayTrait::verifyUnipaySign()` | `unipay_public_cert_path` |
+| 支付宝 | `AlipayTrait::verifyAlipaySign()` | `alipay_public_cert_path` |
 
-### 4. 纯数组 callback 不验签（设计限制）
+**检查点**：
+- CallbackPlugin 是否调用 Trait 提供或 Plugin 自身实现的签名验证方法
+- 签名算法是否与官方文档一致（对照 `@see` 链接）
+- 配置缺失时抛异常
+- 签名为空时抛异常
+- 使用 `hash_equals` 防时序攻击
 
-`getCallbackParams()` 传入数组时不经过签名验证，这是项目级设计决策（所有 Provider 一致）。确认文档中有说明即可。
+### 4. 数组回调的处理
 
-## 一致性检查
+**仅适用于 Stripe/Wechat/Paypal**（构造 `ServerRequest` 并验签）：
 
-### Provider 结构完整性
+`getCallbackParams()` 处理逻辑：
 
-对照 AGENTS.md "新增 Provider 步骤" 逐项检查：
+| 输入类型 | 行为 |
+|----------|------|
+| `['body' => ..., 'headers' => ...]` | 构造带 headers 的 `ServerRequest`，**会验签** |
+| 纯数组（无 headers） | 构造无 headers 的 `ServerRequest`，验签时会抛 `SIGN_EMPTY` |
+| `ServerRequestInterface` | 直接使用，验签 |
+| `null` | 从 `ServerRequest::fromGlobals()` 获取 |
 
-- [ ] `src/Plugin/{Provider}/V{n}/` — 插件
-- [ ] `src/Provider/{Provider}.php` — ProviderInterface 实现
-- [ ] `src/Service/{Provider}ServiceProvider.php` — 服务注册
-- [ ] `src/Shortcut/{Provider}/` — 快捷方式
-- [ ] `src/Functions.php` — 辅助函数（`get_{provider}_url`、`verify_{provider}_sign` 等）
-- [ ] `src/Pay.php` — Provider 注册
-- [ ] `src/Exception/Exception.php` — 异常常量
-- [ ] `tests/` — 与源码结构对应
-- [ ] `web/docs/v3/{provider}/` — 文档
-- [ ] 侧边栏、配置、CHANGELOG 更新
+**结论**：数组回调只有提供完整 `headers` + `body` 才能通过验签；否则验签阶段抛异常。
 
-### 管道一致性
+**Alipay/Douyin/Unipay 不同**：
+- `getCallbackParams()` 返回 `Collection`（从 query/parsedBody 取值）
+- 直接 merge 到 params，不构造 `ServerRequest`
+- CallbackPlugin 从 params 中取值验签
 
-每个 Shortcut 的插件管道应遵循统一模式：
+### 5. 加密资源解密（微信）
+
+微信回调的 `resource` 字段需解密：
 
 ```php
-[
-    StartPlugin::class,
-    ObtainAccessTokenPlugin::class, // 或对应的 token 插件
-    业务Plugin::class,
-    AddPayloadBodyPlugin::class,
-    AddRadarPlugin::class,
-    ResponsePlugin::class,
-    ParserPlugin::class,
-]
+$body['resource'] = self::decryptWechatResource($body['resource'] ?? [], $config);
 ```
 
-后置插件（如 PayConfirmPlugin）放在 ParserPlugin 之后。
+检查 `CallbackPlugin` 是否调用此方法。
+
+---
 
-### 命名与代码规范
+## Phase 4: 架构一致性
 
-| 检查点 | 要求 |
-|--------|------|
-| `declare(strict_types=1)` | 每个文件 |
-| `use` 导入 | 禁止直接写完整命名空间 |
-| 日志格式 | `[Provider][Version][Category][Plugin]`，中文消息 |
-| 异常常量 | `PARAMS_{PROVIDER}_*`、`CONFIG_{PROVIDER}_*` |
-| Plugin 命名 | `{Action}Plugin.php` |
-| Shortcut 命名 | `{Method}Shortcut.php` |
+### 1. 插件管道骨架
 
-## 官方文档对照验证
+**通用骨架**：
+```
+StartPlugin → [前置插件] → 业务插件 → [后置插件] → ParserPlugin
+```
 
-**必须结合代码中的 `@see` 链接和 docs 中的官方文档链接**：
+**各 Provider 差异**：
 
-1. **API 端点 URL** — 每个 Plugin 的 `_url` 是否与官方 API 文档一致
-2. **HTTP 方法** — GET/POST 是否正确
-3. **认证方式** — Header 名称、格式是否与官方一致
-4. **请求/响应字段** — 必填/可选字段是否正确
-5. **签名算法** — 算法、拼接顺序是否与官方文档完全一致
-6. **Base URL** — production/sandbox URL 是否正确
+| Provider | 前置插件 | 后置插件 |
+|----------|----------|----------|
+| Stripe | 无 | `AddRadarPlugin` → `ResponsePlugin` |
+| PayPal | `ObtainAccessTokenPlugin` | `AddPayloadBodyPlugin` → `AddRadarPlugin` → `ResponsePlugin` |
+| 微信 | 无 | `AddPayloadBodyPlugin` → `AddPayloadSignaturePlugin` → `AddRadarPlugin` → `VerifySignaturePlugin` → `ResponsePlugin` |
+| 支付宝 | 无 | `FormatPayloadBizContentPlugin` → `AddPayloadSignaturePlugin` → `AddRadarPlugin` → `VerifySignaturePlugin` → `ResponsePlugin` |
 
-## 文档检查
+**注意**：不同 Provider 管道差异较大，不要按固定模板审查。
 
-- [ ] docs 中的官方链接可访问且指向正确端点（注意 create vs retrieve 混淆）
-- [ ] 示例代码使用原生 PHP，框架无关
-- [ ] 侧边栏已更新
+### 2. mergeCommonPlugins 实现
 
-## 避免重复造轮子
+Provider 类必须实现此方法，返回完整管道：
+
+```php
+public function mergeCommonPlugins(array $plugins): array
+{
+    return array_merge(
+        [StartPlugin::class, /* 前置插件 */],
+        $plugins,
+        [/* 后置插件 */, ParserPlugin::class],
+    );
+}
+```
+
+### 3. Trait 方法复用
+
+新增 Provider 应复用 Trait 方法而非重新实现：
+
+| 功能 | Trait 方法 |
+|------|------------|
+| URL 构建 | `get{Provider}Url()` |
+| 签名验证 | `verify{Provider}WebhookSign()` / `verify{Provider}Sign()` |
+| 配置获取 | `ProviderConfigTrait::getProviderConfig()`、`getTenant()` |
+| 加密解密 | `WechatTrait::decryptWechatResource()` |
+
+### 4. Provider 常量定义
+
+必须定义 `URL` 常量：
+
+```php
+public const URL = [
+    Pay::MODE_NORMAL => 'https://api.xxx.com/',
+    Pay::MODE_SANDBOX => 'https://sandbox.api.xxx.com/',
+    Pay::MODE_SERVICE => 'https://api.xxx.com/',
+];
+```
+
+特殊常量（如微信）：
+- `AUTH_TAG_LENGTH_BYTE`
+- `MCH_SECRET_KEY_LENGTH_BYTE`
+
+### 5. Event 调用
+
+callback 方法必须触发事件：
+
+```php
+// Stripe/Wechat/Paypal（ServerRequestInterface）
+Event::dispatch(new CallbackReceived('provider', clone $request, $params, null));
+
+// Alipay/Douyin/Unipay/Jsb（Collection）
+Event::dispatch(new CallbackReceived('provider', $request->all(), $params, null));
+```
+
+其他方法触发：
 
-检查新增辅助函数是否在 `yansongda/supports` 中已有实现：
-- UUID 生成 → `Str::uuidV4()`
-- 字符串处理 → `Str::*`
-- 集合操作 → `Collection::*`
+```php
+Event::dispatch(new MethodCalled('provider', __METHOD__, $order, null));
+```
+
+### 6. PHPStan ignore 注释
+
+Trait 静态方法调用需添加注释：
+
+```php
+/* @phpstan-ignore-next-line */
+self::verifyWechatSign(...);
+```
+
+这是 PHPStan 对 Trait 静态调用的已知限制，非代码质量问题。
+
+---
+
+## Phase 5: 官方文档对照
+
+结合代码中的 `@see` 链接验证：
+
+| # | 检查点 |
+|---|--------|
+| 1 | API 端点 URL 是否与官方一致 |
+| 2 | HTTP 方法（GET/POST）是否正确 |
+| 3 | 认证 Header 名称、格式是否正确 |
+| 4 | 请求/响应字段（必填/可选）是否正确 |
+| 5 | 签名算法、拼接顺序是否与官方完全一致 |
+| 6 | Base URL（production/sandbox）是否正确 |
+
+---
+
+## Phase 6: 测试覆盖
+
+| # | 检查项 |
+|---|--------|
+| 1 | 每个 Plugin 有对应测试 |
+| 2 | 必填参数缺失的异常测试 |
+| 3 | 可选参数缺失的边界测试 |
+| 4 | 多租户场景（`_config` 参数） |
+| 5 | HTTP client mock，禁止真实 API 调用 |
+| 6 | Callback 签名验证的正向/反向测试 |
+
+---
+
+## Phase 7: 文档完整性
+
+| # | 检查项 |
+|---|--------|
+| 1 | 官方链接可访问且指向正确端点 |
+| 2 | 示例代码使用原生 PHP，框架无关 |
+| 3 | 侧边栏已更新 |
+| 4 | CHANGELOG 已更新 |
+
+---
 
 ## 常见误报
 
-### null-safe 操作符空指针
+### null-safe 操作符
 
 ```php
 $payload?->get('a', $payload->get('b'))
 ```
 
-PHP 8.0 的 null-safe 实现了 **full short-circuiting**：当 `$payload` 为 `null` 时，参数 `$payload->get('b')` **不会被求值**。这不是 bug。
+PHP 8.0 的 null-safe 实现了 **full short-circuiting**：当 `$payload` 为 `null` 时，右侧参数不会被求值。这不是 bug。
 
 参考：[PHP RFC nullsafe_operator](https://wiki.php.net/rfc/nullsafe_operator)
 
-## 测试覆盖检查
+---
+
+## 避免重复造轮子
+
+检查新增功能是否在 `yansongda/supports` 或 `yansongda/artful` 中已有实现：
+
+| 功能 | 已有实现 |
+|------|----------|
+| UUID 生成 | `Str::uuidV4()` |
+| 字符串处理 | `Str::*` |
+| 集合操作 | `Collection::*` |
+| 空值过滤 | `filter_params()` (artful) |
+| HTTP 方法获取 | `get_radar_method()` (artful) |
+| Body 获取 | `get_radar_body()` (artful) |
+
 
-- [ ] 每个 Plugin 有对应测试
-- [ ] 必填参数缺失的异常测试
-- [ ] 可选参数缺失的边界测试（验证 BUG-2 类问题）
-- [ ] 多租户场景（`_config` 参数）
-- [ ] HTTP client mock，禁止真实 API 调用
-- [ ] Callback 签名验证的正向/反向测试
 
 ## Review 报告模板
 
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,11 +1,7 @@
-**Generated:** 2026-04-11
-**Commit:** 5c4c509
-**Branch:** master
-
 # yansongda/pay AGENTS.md
 
 ## OVERVIEW
-PHP 支付 SDK，支持支付宝、微信、银联、抖音、江苏银行、PayPal 等多服务商。项目基于插件管道架构，重点关注支付流程、回调验签和 Provider 扩展一致性。
+PHP 支付 SDK，支持支付宝、微信、银联、抖音、江苏银行、PayPal、Stripe 等多服务商。项目基于插件管道架构，重点关注支付流程、回调验签和 Provider 扩展一致性。
 
 ## STRUCTURE
 ```text
@@ -18,7 +14,6 @@ src/
 ├── Service/
 ├── Shortcut/{Provider}/
 ├── Traits/
-├── Functions.php
 └── Pay.php
 ```
 
@@ -62,7 +57,7 @@ cd web && pnpm web:build
 - **CI 矩阵**：PHP 8.2-8.5 + Laravel/Hyperf/Default
 
 ## 核心架构
-- 插件管道：`StartPlugin → ObtainTokenPlugin → 业务插件 → AddPayloadBodyPlugin → AddRadarPlugin → ResponsePlugin → ParserPlugin`
+- 插件管道：`StartPlugin → [前置插件] → 业务插件 → [后置插件] → ParserPlugin`（各 Provider 差异较大，详见各 Provider 的 `mergeCommonPlugins`）
 - `Rocket`（`Yansongda\Artful\Rocket`）承载 params、payload、radar、destination
 - `PluginInterface` 实现 `assembly(Rocket $rocket, Closure $next): Rocket`
 - `ProviderInterface` 实现 `pay`、`query`、`cancel`、`close`、`refund`、`callback`、`success`
@@ -78,23 +73,24 @@ cd web && pnpm web:build
 |---|---|---|
 | 插件 | `{Action}Plugin.php` | `PayPlugin`、`RefundPlugin` |
 | 快捷方式 | `{Method}Shortcut.php` | `WebShortcut`、`QueryShortcut` |
-| 服务商 | `{ProviderName}.php` | `Paypal.php`、`Alipay.php` |
-| 服务提供者 | `{ProviderName}ServiceProvider.php` | `PaypalServiceProvider.php` |
+| Provider | `{ProviderName}.php` | `Paypal.php`、`Stripe.php` |
+| Trait | `{Provider}Trait.php` | `WechatTrait`、`StripeTrait` |
+| ServiceProvider | `{ProviderName}ServiceProvider.php` | `PaypalServiceProvider.php` |
 | 命名空间 | `Yansongda\Pay\Plugin\{Provider}\V{n}\Pay\{Plugin}` | 版本号与 API 版本一致 |
 
 ### 其他约定
 - PHPStan 忽略：`Illuminate\Container\Container`、`Hyperf\Utils\ApplicationContext`、`think\Container`
 - 日志使用中文消息：`[Provider][Version][Category][Plugin]`
 - 异常在 `src/Exception/Exception.php` 定义常量，使用 `Yansongda\Artful\Exception\*`，消息保持中文
 
-### 辅助函数
-| 函数类型 | 主要函数 |
+### Trait 方法
+| 功能类型 | Trait 方法 |
 |---|---|
-| 配置/租户 | `get_tenant()`、`get_provider_config()` |
-| URL 构建 | `get_alipay_url()`、`get_wechat_url()`、`get_unipay_url()` |
-| 签名验证 | `verify_alipay_sign()`、`verify_wechat_sign()` |
-| 证书处理 | `get_public_cert()`、`get_private_cert()` |
-| 微信专用 | `decrypt_wechat_resource()`、`reload_wechat_public_certs()` |
+| 配置/租户 | `ProviderConfigTrait::getProviderConfig()`、`ProviderConfigTrait::getTenant()` |
+| URL 构建 | `AlipayTrait::getAlipayUrl()`、`WechatTrait::getWechatUrl()`、`UnipayTrait::getUnipayUrl()`、`StripeTrait::getStripeUrl()` |
+| 签名验证 | `AlipayTrait::verifyAlipaySign()`、`WechatTrait::verifyWechatSign()`、`StripeTrait::verifyStripeWebhookSign()` |
+| 证书处理 | `CertManager::getPublicCert()`、`CertManager::getPrivateCert()` |
+| 微信专用 | `WechatTrait::decryptWechatResource()`、`WechatTrait::reloadWechatPublicCerts()` |
 
 ### 测试模式
 ```php
@@ -116,22 +112,27 @@ $httpClient->shouldReceive('sendRequest')->andReturn(new Response(200, [], '{"co
 ## 安全要点
 **所有回调/Webhook 必须验证签名**。
 
-| Provider | 验证方式 |
-|---|---|
-| 支付宝 | 本地 RSA 验证 |
-| 微信 | 本地证书签名验证 |
-| PayPal | 调用 `verify-webhook-signature` API |
-| 抖音 | 本地 SHA1 验证 |
-| 银联 | 本地证书签名验证 |
+| Provider | 验证方式 | Trait 方法 |
+|---|---|---|
+| 支付宝 | 本地 RSA 验证 | `AlipayTrait::verifyAlipaySign()` |
+| 微信 | 本地证书签名验证 | `WechatTrait::verifyWechatSign()` |
+| PayPal | 调用 `verify-webhook-signature` API | `PaypalTrait::verifyPaypalWebhookSign()` |
+| Stripe | 本地 HMAC-SHA256 验证 | `StripeTrait::verifyStripeWebhookSign()` |
+| 抖音 | 本地 SHA1 验证 | —（在 `CallbackPlugin::verifySign()` 中实现） |
+| 银联 | 本地证书签名验证 | `UnipayTrait::verifyUnipaySign()` |
+
+回调处理：
+- **Stripe/Wechat/Paypal**：`callback()` 传递 `_request`（`ServerRequestInterface`）和 `_params` 到 `CallbackPlugin`
+- **Alipay/Douyin/Unipay/Jsb**：通过 `getCallbackParams()` 获取 `Collection`，并 merge 到 params
 
-回调处理：Provider 的 `callback()` 方法传递 `_request`（`ServerRequestInterface`）到 `CallbackPlugin`，由插件负责验证。
+由 `CallbackPlugin` 负责签名验证。
 
 ## 新增 Provider 步骤
 1. 在 `src/Plugin/{Provider}/V{n}/` 下创建插件
 2. 在 `src/Provider/{Provider}.php` 下创建服务商类，实现 `ProviderInterface`
 3. 在 `src/Service/{Provider}ServiceProvider.php` 下创建服务提供者
 4. 在 `src/Shortcut/{Provider}/` 下创建快捷方式
-5. 在 `src/Functions.php` 中添加辅助函数（`get_{provider}_url`、`verify_{provider}_sign` 等）
+5. 在 `src/Traits/{Provider}Trait.php` 中添加 Trait 方法（`get{Provider}Url`、`verify{Provider}WebhookSign` 等）
 6. 在 `src/Pay.php` 中注册服务商
 7. 在 `src/Exception/Exception.php` 中添加异常常量
 8. 在 `tests/` 下添加与源码结构对应的测试
PATCH

echo "Gold patch applied."
