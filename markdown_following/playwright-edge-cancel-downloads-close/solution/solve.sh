#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'Ongoing downloads cause crashes in Edge' packages/playwright-core/src/server/chromium/crBrowser.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply changes to download.ts
cat > /tmp/download_new.ts << 'DOWNLOADEOF'
/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import path from 'path';

import { Page } from './page';
import { assert } from '../utils';
import { Artifact } from './artifact';

export class Download {
  readonly artifact: Artifact;
  readonly url: string;
  private _uuid: string;
  private _page: Page;
  private _suggestedFilename: string | undefined;

  constructor(page: Page, downloadsPath: string, uuid: string, url: string, suggestedFilename?: string, downloadFilename?: string) {
    const unaccessibleErrorMessage = page.browserContext._options.acceptDownloads === 'deny' ? 'Pass { acceptDownloads: true } when you are creating your browser context.' : undefined;
    const downloadPath = path.join(downloadsPath, downloadFilename ?? uuid);
    this.artifact = new Artifact(page, downloadPath, unaccessibleErrorMessage, () => this.cancel());
    this._page = page;
    this.url = url;
    this._uuid = uuid;
    this._suggestedFilename = suggestedFilename;
    // Note: downloads are never removed from the context, so that we can delete them upon context closure.
    page.browserContext._downloads.add(this);
    if (suggestedFilename !== undefined)
      this._fireDownloadEvent();
  }

  cancel() {
    return this._page.browserContext.cancelDownload(this._uuid);
  }

  filenameSuggested(suggestedFilename: string) {
    assert(this._suggestedFilename === undefined);
    this._suggestedFilename = suggestedFilename;
    this._fireDownloadEvent();
  }

  suggestedFilename(): string {
    return this._suggestedFilename!;
  }

  private _fireDownloadEvent() {
    this._page.instrumentation.onDownload(this._page, this);
    this._page.emit(Page.Events.Download, this);
  }
}
DOWNLOADEOF

cp /tmp/download_new.ts packages/playwright-core/src/server/download.ts

# Apply changes to crBrowser.ts using perl for precise replacement
perl -i -pe '
if (/await this._browser._session.send\(.Target.disposeBrowserContext./) {
    $_ = "    // Ongoing downloads cause crashes in Edge, so cancel them first.\n    await Promise.all([...this._downloads].map(download => download.cancel().catch(() => {})));\n\n" . $_;
}
' packages/playwright-core/src/server/chromium/crBrowser.ts

echo "Patch applied successfully."
