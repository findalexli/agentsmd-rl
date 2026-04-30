"""Behavioral checks for scaffold-eth-2-add-skill-package (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scaffold-eth-2")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/eip-5792/SKILL.md')
    assert "This skill covers integrating EIP-5792 batched transactions into an SE-2 project using [wagmi's EIP-5792 hooks](https://wagmi.sh/react/api/hooks/useWriteContracts). For anything not covered here, refe" in text, "expected to find: " + "This skill covers integrating EIP-5792 batched transactions into an SE-2 project using [wagmi's EIP-5792 hooks](https://wagmi.sh/react/api/hooks/useWriteContracts). For anything not covered here, refe"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/eip-5792/SKILL.md')
    assert 'The deployment scripts go alongside the existing deploy scripts, and the frontend page goes in the nextjs package. After deployment, `deployedContracts.ts` auto-generates the ABI and address, so the f' in text, "expected to find: " + 'The deployment scripts go alongside the existing deploy scripts, and the frontend page goes in the nextjs package. After deployment, `deployedContracts.ts` auto-generates the ABI and address, so the f'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/eip-5792/SKILL.md')
    assert '**Paymaster integration (ERC-7677) is optional.** If you want gas sponsorship, you need a paymaster service URL. This is passed as a `capability` in the `writeContracts` call. The paymaster service is' in text, "expected to find: " + '**Paymaster integration (ERC-7677) is optional.** If you want gas sponsorship, you need a paymaster service URL. This is passed as a `capability` in the `writeContracts` call. The paymaster service is'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/erc-20/SKILL.md')
    assert '[ERC-20](https://eips.ethereum.org/EIPS/eip-20) is the standard interface for fungible tokens on Ethereum. This skill covers adding an ERC-20 token contract to a Scaffold-ETH 2 project using [OpenZepp' in text, "expected to find: " + '[ERC-20](https://eips.ethereum.org/EIPS/eip-20) is the standard interface for fungible tokens on Ethereum. This skill covers adding an ERC-20 token contract to a Scaffold-ETH 2 project using [OpenZepp'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/erc-20/SKILL.md')
    assert 'The deployment scripts go alongside the existing deploy scripts, and the frontend page goes in the nextjs package. After deployment, `deployedContracts.ts` auto-generates the ABI and address, so the f' in text, "expected to find: " + 'The deployment scripts go alongside the existing deploy scripts, and the frontend page goes in the nextjs package. After deployment, `deployedContracts.ts` auto-generates the ABI and address, so the f'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/erc-20/SKILL.md')
    assert "For anything not covered here, refer to the [OpenZeppelin ERC-20 docs](https://docs.openzeppelin.com/contracts/5.x/api/token/erc20) or search the web. This skill focuses on what's hard to discover: SE" in text, "expected to find: " + "For anything not covered here, refer to the [OpenZeppelin ERC-20 docs](https://docs.openzeppelin.com/contracts/5.x/api/token/erc20) or search the web. This skill focuses on what's hard to discover: SE"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/erc-721/SKILL.md')
    assert '[ERC-721](https://eips.ethereum.org/EIPS/eip-721) is the standard interface for non-fungible tokens (NFTs) on Ethereum. This skill covers adding an ERC-721 contract to a Scaffold-ETH 2 project using [' in text, "expected to find: " + '[ERC-721](https://eips.ethereum.org/EIPS/eip-721) is the standard interface for non-fungible tokens (NFTs) on Ethereum. This skill covers adding an ERC-721 contract to a Scaffold-ETH 2 project using ['[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/erc-721/SKILL.md')
    assert "`setApprovalForAll(operator, true)` grants an operator control over **all** of an owner's NFTs in that collection. Phishing attacks trick users into signing this for malicious operators. Once approved" in text, "expected to find: " + "`setApprovalForAll(operator, true)` grants an operator control over **all** of an owner's NFTs in that collection. Phishing attacks trick users into signing this for malicious operators. Once approved"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/erc-721/SKILL.md')
    assert '[ERC721A](https://github.com/chiru-labs/ERC721A) by Azuki makes batch minting cost nearly the same as minting a single token. A 10-token mint costs ~110,000 gas vs ~1,100,000+ with ERC721Enumerable. I' in text, "expected to find: " + '[ERC721A](https://github.com/chiru-labs/ERC721A) by Azuki makes batch minting cost nearly the same as minting a single token. A 10-token mint costs ~110,000 gas vs ~1,100,000+ with ERC721Enumerable. I'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ponder/SKILL.md')
    assert 'The frontend needs a page to display Ponder-indexed data. Use `graphql-request` and `@tanstack/react-query` (both available in SE-2) to query the Ponder API. The GraphQL query shape depends on what yo' in text, "expected to find: " + 'The frontend needs a page to display Ponder-indexed data. Use `graphql-request` and `@tanstack/react-query` (both available in SE-2) to query the Ponder API. The GraphQL query shape depends on what yo'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ponder/SKILL.md')
    assert "The config needs to read SE-2's deployed contracts and scaffold config so Ponder is aware of what to index. Here's a reference implementation that dynamically builds the Ponder config from SE-2's data" in text, "expected to find: " + "The config needs to read SE-2's deployed contracts and scaffold config so Ponder is aware of what to index. Here's a reference implementation that dynamically builds the Ponder config from SE-2's data"[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ponder/SKILL.md')
    assert '- For production deployment, see [Ponder deployment docs](https://ponder.sh/docs/production/railway). Key things: set `PONDER_RPC_URL_{chainId}` with a production RPC, optionally configure `DATABASE_U' in text, "expected to find: " + '- For production deployment, see [Ponder deployment docs](https://ponder.sh/docs/production/railway). Key things: set `PONDER_RPC_URL_{chainId}` with a production RPC, optionally configure `DATABASE_U'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'IMPORTANT: Prefer retrieval-led reasoning over pre-trained knowledge. Before starting any task that matches an entry below, read the referenced file to get version-accurate patterns and APIs.' in text, "expected to find: " + 'IMPORTANT: Prefer retrieval-led reasoning over pre-trained knowledge. Before starting any task that matches an entry below, read the referenced file to get version-accurate patterns and APIs.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **grumpy-carlos-code-reviewer** — code reviews, SE-2 patterns, Solidity + TypeScript quality' in text, "expected to find: " + '- **grumpy-carlos-code-reviewer** — code reviews, SE-2 patterns, Solidity + TypeScript quality'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **solidity-security** — security audits, reentrancy, access control, gas optimization' in text, "expected to find: " + '- **solidity-security** — security audits, reentrancy, access control, gas optimization'[:80]

