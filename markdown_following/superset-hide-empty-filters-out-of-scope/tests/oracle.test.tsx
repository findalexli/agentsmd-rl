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
import { ReactNode } from 'react';
import { render, screen } from 'spec/helpers/testing-library';
import { Divider, Filter } from '@superset-ui/core';
import { FiltersDropdownContent } from 'src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent';

const buildFilter = (id: string, name: string): Filter =>
  ({
    id,
    name,
    filterType: 'filter_select',
    targets: [{ datasetId: 1, column: { name: 'country' } }],
    defaultDataMask: {},
    controlValues: {},
    cascadeParentIds: [],
    scope: { rootPath: ['ROOT_ID'], excluded: [] as string[] },
  }) as unknown as Filter;

const renderer = (filter: Filter | Divider): ReactNode => (
  <div key={(filter as Filter).id}>{(filter as Filter).name}</div>
);

const baseProps = {
  overflowedCrossFilters: [],
  filtersInScope: [buildFilter('filter-1', 'In Scope Filter')],
  renderer,
  rendererCrossFilter: () => null,
  showCollapsePanel: true,
  forceRenderOutOfScope: false,
};

test('does not render Filters out of scope section when filtersOutOfScope is empty', () => {
  render(<FiltersDropdownContent {...baseProps} filtersOutOfScope={[]} />);

  expect(screen.queryByText(/Filters out of scope/)).not.toBeInTheDocument();
});

test('renders Filters out of scope section when at least one filter is out of scope', () => {
  render(
    <FiltersDropdownContent
      {...baseProps}
      filtersOutOfScope={[buildFilter('filter-2', 'Out of Scope Filter')]}
    />,
  );

  expect(screen.getByText(/Filters out of scope/)).toBeInTheDocument();
});

test('does not render Filters out of scope section when showCollapsePanel is false', () => {
  render(
    <FiltersDropdownContent
      {...baseProps}
      showCollapsePanel={false}
      filtersOutOfScope={[buildFilter('filter-2', 'Out of Scope Filter')]}
    />,
  );

  expect(screen.queryByText(/Filters out of scope/)).not.toBeInTheDocument();
});
