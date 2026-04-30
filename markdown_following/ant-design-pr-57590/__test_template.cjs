'
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const projectRoot = process.cwd();
const testFile = path.join(projectRoot, '__conditional_render.test.tsx');

const testContent = `
import React from 'react';
import { render, act } from '@testing-library/react';
import { PureContent } from './components/notification/PurePanel';

describe('PureContent conditional rendering', () => {
  it('should NOT render title div when title is not provided', async () => {
    let container;
    await act(async () => {
      const result = render(
        <PureContent
          prefixCls="ant-notification"
          className=""
          title={undefined}
          description="Test description"
        />
      );
      container = result.container;
    });

    const titleDivs = container.querySelectorAll('.ant-notification-title');
    if (titleDivs.length !== 0) {
      console.log('FAIL: Title div rendered when title is undefined');
      process.exit(1);
    }

    const descDivs = container.querySelectorAll('.ant-notification-description');
    if (descDivs.length !== 1) {
      console.log('FAIL: Description div not found');
      process.exit(1);
    }

    console.log('PASS');
    process.exit(0);
  });

  it('should render title div when title IS provided', async () => {
    let container;
    await act(async () => {
      const result = render(
        <PureContent
          prefixCls="ant-notification"
          className=""
          title="Test Title"
          description="Test description"
        />
      );
      container = result.container;
    });

    const titleDivs = container.querySelectorAll('.ant-notification-title');
    if (titleDivs.length !== 1) {
      console.log('FAIL: Title div not rendered when title is provided');
      process.exit(1);
    }

    console.log('PASS');
    process.exit(0);
  });
});
`;

// Write the test file
fs.writeFileSync(testFile, testContent);

try {
  execSync('npx jest __conditional_render.test.tsx --testPathIgnorePatterns=[] --no-coverage --passWithNoTests', {
    cwd: projectRoot,
    stdio: 'pipe',
    timeout: 120
  });
  console.log('PASS');
  process.exit(0);
} catch (e) {
  const output = e.stdout ? e.stdout.toString() : e.stderr ? e.stderr.toString() : '';
  if (output.includes('PASS')) {
    console.log('PASS');
    process.exit(0);
  }
  console.log('FAIL: ' + output.substring(0, 500));
  process.exit(1);
} finally {
  try { fs.unlinkSync(testFile); } catch (e) {}
}
