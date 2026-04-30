/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import {
  type AnyThemeConfig,
  Theme,
  ThemeAlgorithm,
  ThemeMode,
} from '@apache-superset/core/theme';
import type {
  BootstrapThemeDataConfig,
  CommonBootstrapData,
} from 'src/types/bootstrapTypes';
import getBootstrapData from 'src/utils/getBootstrapData';
import { ThemeController } from 'src/theme/ThemeController';

jest.mock('src/utils/getBootstrapData');
const mockGetBootstrapData = getBootstrapData as jest.MockedFunction<
  typeof getBootstrapData
>;

const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

const mockMatchMedia = jest.fn();
const mockThemeFromConfig = jest.fn();
const mockSetConfig = jest.fn();

const DEFAULT_THEME: AnyThemeConfig = {
  token: {
    colorBgBase: '#ededed',
    colorTextBase: '#120f0f',
    colorLink: '#0062ec',
    colorPrimary: '#c96f0f',
    colorInfo: '#c96f0f',
    colorSuccess: '#3c7c1b',
    colorWarning: '#dc9811',
  },
};

const DARK_THEME: AnyThemeConfig = {
  token: {
    colorBgBase: '#141118',
    colorTextBase: '#fdc7c7',
    colorLink: '#0062ec',
    colorPrimary: '#c96f0f',
    colorInfo: '#c96f0f',
    colorSuccess: '#3c7c1b',
    colorWarning: '#dc9811',
  },
  algorithm: ThemeAlgorithm.DARK,
};

const createMockBootstrapData = (
  themeConfig: BootstrapThemeDataConfig = {
    default: DEFAULT_THEME,
    dark: DARK_THEME,
  },
): { common: CommonBootstrapData } => ({
  common: {
    application_root: '/',
    static_assets_prefix: '/static/assets/',
    conf: {},
    locale: 'en',
    feature_flags: {},
    language_pack: {},
    extra_categorical_color_schemes: [],
    extra_sequential_color_schemes: [],
    theme: themeConfig,
    menu_data: {},
    d3_format: {},
    d3_time_format: {},
  } as any as CommonBootstrapData,
});

const mockThemeObject = {
  setConfig: mockSetConfig,
  theme: DEFAULT_THEME,
} as unknown as Theme;

const createController = (
  options: Partial<ConstructorParameters<typeof ThemeController>[0]> = {},
) =>
  new ThemeController({
    themeObject: mockThemeObject,
    ...options,
  });

const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

beforeEach(() => {
  jest.clearAllMocks();

  Object.defineProperty(window, 'localStorage', {
    value: mockLocalStorage,
    writable: true,
  });

  Object.defineProperty(window, 'matchMedia', {
    value: mockMatchMedia,
    writable: true,
  });

  mockMatchMedia.mockReturnValue({
    matches: false,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  });

  mockSetConfig.mockImplementation(() => {});
  mockThemeFromConfig.mockReturnValue(mockThemeObject);

  (Theme as any).fromConfig = mockThemeFromConfig;

  mockLocalStorage.getItem.mockReturnValue(null);
  mockLocalStorage.setItem.mockImplementation(() => {});
  mockLocalStorage.removeItem.mockImplementation(() => {});

  mockGetBootstrapData.mockReturnValue(createMockBootstrapData());
});

afterAll(() => {
  consoleWarnSpy.mockRestore();
  consoleErrorSpy.mockRestore();
});

test('initialMode_used_when_no_saved_mode', () => {
  mockGetBootstrapData.mockReturnValue(
    createMockBootstrapData({
      default: DEFAULT_THEME,
      dark: DARK_THEME,
    }),
  );

  const controller = createController({ initialMode: ThemeMode.DEFAULT });

  expect(controller.getCurrentMode()).toBe(ThemeMode.DEFAULT);
});

test('no_initialMode_defaults_to_system', () => {
  mockGetBootstrapData.mockReturnValue(
    createMockBootstrapData({
      default: DEFAULT_THEME,
      dark: DARK_THEME,
    }),
  );

  const controller = createController();

  expect(controller.getCurrentMode()).toBe(ThemeMode.SYSTEM);
});

test('saved_mode_takes_precedence_over_initialMode', () => {
  mockGetBootstrapData.mockReturnValue(
    createMockBootstrapData({
      default: DEFAULT_THEME,
      dark: DARK_THEME,
    }),
  );

  mockLocalStorage.getItem.mockReturnValue(ThemeMode.DARK);

  const controller = createController({ initialMode: ThemeMode.DEFAULT });

  expect(controller.getCurrentMode()).toBe(ThemeMode.DARK);
});

test('initialMode_default_overrides_system_dark_preference', () => {
  mockGetBootstrapData.mockReturnValue(
    createMockBootstrapData({
      default: DEFAULT_THEME,
      dark: DARK_THEME,
    }),
  );

  mockMatchMedia.mockReturnValue({
    matches: true,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  });

  const controller = createController({ initialMode: ThemeMode.DEFAULT });

  expect(controller.getCurrentMode()).toBe(ThemeMode.DEFAULT);
  const lastCall =
    mockSetConfig.mock.calls[mockSetConfig.mock.calls.length - 1][0];
  expect(lastCall.token.colorBgBase).toBe(DEFAULT_THEME.token!.colorBgBase);
});

test('setThemeMode_works_after_init_with_initialMode', () => {
  mockGetBootstrapData.mockReturnValue(
    createMockBootstrapData({
      default: DEFAULT_THEME,
      dark: DARK_THEME,
    }),
  );

  const controller = createController({ initialMode: ThemeMode.DEFAULT });
  expect(controller.getCurrentMode()).toBe(ThemeMode.DEFAULT);

  controller.setThemeMode(ThemeMode.DARK);
  expect(controller.getCurrentMode()).toBe(ThemeMode.DARK);

  controller.setThemeMode(ThemeMode.SYSTEM);
  expect(controller.getCurrentMode()).toBe(ThemeMode.SYSTEM);
});

test('initialMode_ignored_when_no_dark_theme', () => {
  mockGetBootstrapData.mockReturnValue(
    createMockBootstrapData({
      default: DEFAULT_THEME,
      dark: {},
    }),
  );

  const controller = createController({ initialMode: ThemeMode.SYSTEM });

  expect(controller.getCurrentMode()).toBe(ThemeMode.DEFAULT);
});

test('invalid_initialMode_falls_back_to_system', () => {
  mockGetBootstrapData.mockReturnValue(
    createMockBootstrapData({
      default: DEFAULT_THEME,
      dark: DARK_THEME,
    }),
  );

  const controller = createController({
    initialMode: 'bogus' as ThemeMode,
  });

  expect(controller.getCurrentMode()).toBe(ThemeMode.SYSTEM);
});
