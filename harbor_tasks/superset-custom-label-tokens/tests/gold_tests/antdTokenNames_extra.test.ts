/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.
 */
import {
  isValidTokenName,
  isSupersetCustomToken,
} from './antdTokenNames';

test('label variant tokens are recognized as valid Superset custom tokens', () => {
  const labelTokens = [
    // Published/Draft
    'labelPublishedColor',
    'labelPublishedBg',
    'labelPublishedBorderColor',
    'labelPublishedIconColor',
    'labelDraftColor',
    'labelDraftBg',
    'labelDraftBorderColor',
    'labelDraftIconColor',
    // Dataset type
    'labelDatasetPhysicalColor',
    'labelDatasetPhysicalBg',
    'labelDatasetPhysicalBorderColor',
    'labelDatasetPhysicalIconColor',
    'labelDatasetVirtualColor',
    'labelDatasetVirtualBg',
    'labelDatasetVirtualBorderColor',
    'labelDatasetVirtualIconColor',
  ];

  labelTokens.forEach(token => {
    expect(isValidTokenName(token)).toBe(true);
    expect(isSupersetCustomToken(token)).toBe(true);
  });
});
