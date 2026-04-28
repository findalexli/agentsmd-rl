"""Behavioral checks for libtorrent-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/libtorrent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '`simulation/` contains network simulation tests that use `libsimulator` (a deterministic virtual network). These test high-level behaviors (swarms, DHT, session management) without real network access' in text, "expected to find: " + '`simulation/` contains network simulation tests that use `libsimulator` (a deterministic virtual network). These test high-level behaviors (swarms, DHT, session management) without real network access'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Avoid raw `int` for indices and flags; use `aux::strong_typedef` (`include/libtorrent/units.hpp`) and `flags::bitfield_flag` (`include/libtorrent/flags.hpp`). See `.claude/rules/strong-types.md` for d' in text, "expected to find: " + 'Avoid raw `int` for indices and flags; use `aux::strong_typedef` (`include/libtorrent/units.hpp`) and `flags::bitfield_flag` (`include/libtorrent/flags.hpp`). See `.claude/rules/strong-types.md` for d'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- `settings_pack` enum values must be appended at the end of each enum group (int, bool, string) — never inserted in the middle — to avoid changing the numeric values of existing settings and breaking' in text, "expected to find: " + '- `settings_pack` enum values must be appended at the end of each enum group (int, bool, string) — never inserted in the middle — to avoid changing the numeric values of existing settings and breaking'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/dht.md')
    assert 'All messages are bencoded dicts with mandatory keys `"t"` (transaction id), `"y"` (`"q"/"r"/"e"`), optional `"v"` (version), `"ip"` (external address, BEP 42), `"ro"` (read-only, BEP 5).' in text, "expected to find: " + 'All messages are bencoded dicts with mandatory keys `"t"` (transaction id), `"y"` (`"q"/"r"/"e"`), optional `"v"` (version), `"ip"` (external address, BEP 42), `"ro"` (read-only, BEP 5).'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/dht.md')
    assert '`obfuscated_get_peers`: wraps `get_peers`, uses a random target until convergence, then switches to the real info_hash (BEP 5 privacy mode, controlled by `dht_privacy_lookups`).' in text, "expected to find: " + '`obfuscated_get_peers`: wraps `get_peers`, uses a random target until convergence, then switches to the real info_hash (BEP 5 privacy mode, controlled by `dht_privacy_lookups`).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/dht.md')
    assert 'All DHT code runs on the **session network thread** (boost.asio). No locking needed inside DHT classes. `rpc_manager` uses a mutex only for its observer-pool allocator.' in text, "expected to find: " + 'All DHT code runs on the **session network thread** (boost.asio). No locking needed inside DHT classes. `rpc_manager` uses a mutex only for its observer-pool allocator.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/disk-cache.md')
    assert '- `disk_cache` — the cache itself; holds a `boost::multi_index_container` of `cached_piece_entry` objects, protected by a single `std::mutex`. The container has five indices: by `piece_location` (orde' in text, "expected to find: " + '- `disk_cache` — the cache itself; holds a `boost::multi_index_container` of `cached_piece_entry` objects, protected by a single `std::mutex`. The container has five indices: by `piece_location` (orde'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/disk-cache.md')
    assert 'Flags are stored in `cached_piece_flags flags` (a `bitfield_flag<uint8_t>` bitfield). The mutex must be held to read or modify flags; updates go through `view.modify()` (required by `boost::multi_inde' in text, "expected to find: " + 'Flags are stored in `cached_piece_flags flags` (a `bitfield_flag<uint8_t>` bitfield). The mutex must be held to read or modify flags; updates go through `view.modify()` (required by `boost::multi_inde'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/disk-cache.md')
    assert '- `flushing_flag` — set under the mutex by the thread about to write blocks to disk. While set, that thread has exclusive access to the block buffers being flushed. No other thread will attempt to flu' in text, "expected to find: " + '- `flushing_flag` — set under the mutex by the thread about to write blocks to disk. While set, that thread has exclusive access to the block buffers being flushed. No other thread will attempt to flu'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/piece-picker.md')
    assert '- `info_idx` (`uint16_t`) — index into `m_block_info`; the slice `[info_idx * blocks_per_piece, (info_idx+1) * blocks_per_piece)` holds the block states for this piece' in text, "expected to find: " + '- `info_idx` (`uint16_t`) — index into `m_block_info`; the slice `[info_idx * blocks_per_piece, (info_idx+1) * blocks_per_piece)` holds the block states for this piece'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/piece-picker.md')
    assert '- `locked` (1 bit) — blocks cannot be picked; set during error recovery, cleared by `restore_piece()`' in text, "expected to find: " + '- `locked` (1 bit) — blocks cannot be picked; set during error recovery, cleared by `restore_piece()`'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/piece-picker.md')
    assert 'order (rarest-first is approximated by the priority formula, not by sorting on availability alone).' in text, "expected to find: " + 'order (rarest-first is approximated by the priority formula, not by sorting on availability alone).'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/python-bindings.md')
    assert 'The type stub file is `bindings/python/libtorrent/__init__.pyi`. It was originally bootstrapped with `stubgen` but is now **maintained entirely by hand** — do not regenerate it with stubgen, as that w' in text, "expected to find: " + 'The type stub file is `bindings/python/libtorrent/__init__.pyi`. It was originally bootstrapped with `stubgen` but is now **maintained entirely by hand** — do not regenerate it with stubgen, as that w'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/python-bindings.md')
    assert 'Prefer exposing real C++ classes via boost.python rather than converting them to plain Python dicts. Earlier versions of the bindings returned plain `dict` objects for things like peer info and torren' in text, "expected to find: " + 'Prefer exposing real C++ classes via boost.python rather than converting them to plain Python dicts. Earlier versions of the bindings returned plain `dict` objects for things like peer info and torren'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/python-bindings.md')
    assert 'There is a roughly one-to-one correspondence between `src/foo.cpp` and `tests/foo_test.py`. Tests must be isolated — no real network access, no persistent filesystem side-effects. Use `get_isolated_se' in text, "expected to find: " + 'There is a roughly one-to-one correspondence between `src/foo.cpp` and `tests/foo_test.py`. Tests must be isolated — no real network access, no persistent filesystem side-effects. Use `get_isolated_se'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/strong-types.md')
    assert '`aux::strong_typedef<UnderlyingType, Tag>` wraps an integer so it is incompatible with other integers and other strong types. Arithmetic with raw integers is not allowed; only arithmetic with the same' in text, "expected to find: " + '`aux::strong_typedef<UnderlyingType, Tag>` wraps an integer so it is incompatible with other integers and other strong types. Arithmetic with raw integers is not allowed; only arithmetic with the same'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/strong-types.md')
    assert '`flags::bitfield_flag<UnderlyingType, Tag>` wraps an unsigned integer as a type-safe bitfield. Flags of different types cannot be combined. Individual bit constants are defined using the `_bit` user-d' in text, "expected to find: " + '`flags::bitfield_flag<UnderlyingType, Tag>` wraps an unsigned integer as a type-safe bitfield. Flags of different types cannot be combined. Individual bit constants are defined using the `_bit` user-d'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/strong-types.md')
    assert 'The codebase avoids using raw `int` or bare integers for indices and flags. Instead, use the strong type and flag facilities.' in text, "expected to find: " + 'The codebase avoids using raw `int` or bare integers for indices and flags. Instead, use the strong type and flag facilities.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/v2-torrents.md')
    assert '- `add_hashes()`: receives hashes + uncle proof chain, calls `merkle_validate_and_insert_proofs()`, inserts valid nodes, reports `pass`/`fail` per piece' in text, "expected to find: " + '- `add_hashes()`: receives hashes + uncle proof chain, calls `merkle_validate_and_insert_proofs()`, inserts valid nodes, reports `pass`/`fail` per piece'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/v2-torrents.md')
    assert '`m_block_verified` bitfield tracks which block hashes have been validated against their parent chain up to the known root.' in text, "expected to find: " + '`m_block_verified` bitfield tracks which block hashes have been validated against their parent chain up to the known root.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/v2-torrents.md')
    assert 'Merkle trees are persisted across sessions in resume data (`src/write_resume_data.cpp`, `src/read_resume_data.cpp`):' in text, "expected to find: " + 'Merkle trees are persisted across sessions in resume data (`src/write_resume_data.cpp`, `src/read_resume_data.cpp`):'[:80]

