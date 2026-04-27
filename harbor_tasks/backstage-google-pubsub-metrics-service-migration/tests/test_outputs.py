"""Tests for the MetricsService migration in the google-pubsub events module."""
import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/backstage")
PLUGIN = REPO / "plugins/events-backend-module-google-pubsub"

# Probe test that calls each publisher's constructor with a mocked
# MetricsService and asserts the constructor used it. This file is written
# into the plugin's src/ directory at test time and run via jest.
MIGRATION_PROBE_TS = '''/*
 * Copyright 2026 The Backstage Authors
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

import { mockServices } from '@backstage/backend-test-utils';
import { metricsServiceMock } from '@backstage/backend-test-utils/alpha';
import { GooglePubSubConsumingEventPublisher } from './GooglePubSubConsumingEventPublisher/GooglePubSubConsumingEventPublisher';
import { EventConsumingGooglePubSubPublisher } from './EventConsumingGooglePubSubPublisher/EventConsumingGooglePubSubPublisher';

describe('MetricsService migration', () => {
  it('GooglePubSubConsumingEventPublisher creates counter via injected MetricsService', () => {
    const metrics = metricsServiceMock.mock();
    const logger = mockServices.logger.mock();
    const events = mockServices.events.mock();

    const pubSubFactory = jest.fn(() => ({} as any));

    const Ctor = GooglePubSubConsumingEventPublisher as any;
    const instance = new Ctor({
      logger,
      events,
      metrics,
      tasks: [],
      pubSubFactory,
    });
    expect(instance).toBeDefined();

    expect(metrics.createCounter).toHaveBeenCalledWith(
      'events.google.pubsub.consumer.messages.total',
      expect.objectContaining({ unit: '{message}' }),
    );
  });

  it('EventConsumingGooglePubSubPublisher creates counter via injected MetricsService', () => {
    const metrics = metricsServiceMock.mock();
    const logger = mockServices.logger.mock();
    const events = mockServices.events.mock();

    const pubSubFactory = jest.fn(() => ({} as any));

    const Ctor = EventConsumingGooglePubSubPublisher as any;
    const instance = new Ctor({
      logger,
      events,
      metrics,
      tasks: [],
      pubSubFactory,
    });
    expect(instance).toBeDefined();

    expect(metrics.createCounter).toHaveBeenCalledWith(
      'events.google.pubsub.publisher.messages.total',
      expect.objectContaining({ unit: '{message}' }),
    );
  });
});
'''


def _yarn_env():
    env = os.environ.copy()
    env["CI"] = "1"
    return env


def _inject_migration_test():
    """Place the migration probe test inside the plugin's src/ directory."""
    dst = PLUGIN / "src" / "MetricsMigration.test.ts"
    dst.write_text(MIGRATION_PROBE_TS)


def _run_migration_jest():
    _inject_migration_test()
    return subprocess.run(
        ["yarn", "backstage-cli", "package", "test",
         "--testPathPatterns=MetricsMigration", "--ci"],
        cwd=PLUGIN, capture_output=True, text=True,
        timeout=300, env=_yarn_env(),
    )


def test_consumer_uses_injected_metrics_service():
    """`GooglePubSubConsumingEventPublisher` calls
    `options.metrics.createCounter` with the consumer counter name and unit
    `{message}`."""
    r = _run_migration_jest()
    output = r.stdout + r.stderr
    line = ("✓ GooglePubSubConsumingEventPublisher creates counter via "
            "injected MetricsService")
    assert line in output, (
        f"Consumer migration probe did not pass.\nstdout:\n{r.stdout[-3000:]}"
        f"\nstderr:\n{r.stderr[-3000:]}"
    )


def test_publisher_uses_injected_metrics_service():
    """`EventConsumingGooglePubSubPublisher` calls
    `options.metrics.createCounter` with the publisher counter name and unit
    `{message}`."""
    r = _run_migration_jest()
    output = r.stdout + r.stderr
    line = ("✓ EventConsumingGooglePubSubPublisher creates counter via "
            "injected MetricsService")
    assert line in output, (
        f"Publisher migration probe did not pass.\nstdout:\n{r.stdout[-3000:]}"
        f"\nstderr:\n{r.stderr[-3000:]}"
    )


def test_opentelemetry_dependency_removed():
    """The plugin's `package.json` no longer depends on `@opentelemetry/api`."""
    pkg = json.loads((PLUGIN / "package.json").read_text())
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    assert "@opentelemetry/api" not in deps, (
        f"@opentelemetry/api should be removed from package.json deps, "
        f"got: {sorted(deps.keys())}"
    )


def test_existing_unit_tests_pass():
    """All existing jest tests in this plugin pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "backstage-cli", "package", "test",
         "--testPathIgnorePatterns=MetricsMigration", "--ci"],
        cwd=PLUGIN, capture_output=True, text=True,
        timeout=300, env=_yarn_env(),
    )
    assert r.returncode == 0, (
        f"Existing unit tests failed.\nstdout:\n{r.stdout[-3000:]}"
        f"\nstderr:\n{r.stderr[-3000:]}"
    )


def test_repo_lint_passes():
    """The plugin's lint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "backstage-cli", "package", "lint"],
        cwd=PLUGIN, capture_output=True, text=True,
        timeout=300, env=_yarn_env(),
    )
    assert r.returncode == 0, (
        f"Lint failed.\nstdout:\n{r.stdout[-2000:]}"
        f"\nstderr:\n{r.stderr[-2000:]}"
    )
