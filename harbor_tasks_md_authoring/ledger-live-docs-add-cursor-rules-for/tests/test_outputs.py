"""Behavioral checks for ledger-live-docs-add-cursor-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ledger-live")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/redux-slice.mdc')
    assert 'export const selectStatus = (state: RootState) => state.myFeature.status;' in text, "expected to find: " + 'export const selectStatus = (state: RootState) => state.myFeature.status;'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/redux-slice.mdc')
    assert 'export const selectValue = (state: RootState) => state.myFeature.value;' in text, "expected to find: " + 'export const selectValue = (state: RootState) => state.myFeature.value;'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/redux-slice.mdc')
    assert 'setStatus: (state, action: PayloadAction<MyState["status"]>) => {' in text, "expected to find: " + 'setStatus: (state, action: PayloadAction<MyState["status"]>) => {'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rtk-query-api.mdc')
    assert 'import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";' in text, "expected to find: " + 'import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rtk-query-api.mdc')
    assert '- Type both response and argument: `build.query<ResponseType, ArgType>`' in text, "expected to find: " + '- Type both response and argument: `build.query<ResponseType, ArgType>`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rtk-query-api.mdc')
    assert 'transformResponse: (response: ApiResponse) => response.data.items,' in text, "expected to find: " + 'transformResponse: (response: ApiResponse) => response.data.items,'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/zod-schemas.mdc')
    assert 'Define types in `state-manager/types.ts` using Zod schemas for runtime validation.' in text, "expected to find: " + 'Define types in `state-manager/types.ts` using Zod schemas for runtime validation.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/zod-schemas.mdc')
    assert 'import { ItemListResponseSchema, type ItemListResponse } from "./types";' in text, "expected to find: " + 'import { ItemListResponseSchema, type ItemListResponse } from "./types";'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/zod-schemas.mdc')
    assert 'export type ItemListResponse = z.infer<typeof ItemListResponseSchema>;' in text, "expected to find: " + 'export type ItemListResponse = z.infer<typeof ItemListResponseSchema>;'[:80]

