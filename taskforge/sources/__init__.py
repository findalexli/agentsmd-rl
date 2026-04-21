"""External candidate-task sources for taskforge.

Source adapters normalize upstream benchmark rows, Git history candidates, and
synthetic generators into taskforge-owned task artifacts. Upstream projects
should not write final harbor task directories directly.
"""

from taskforge.sources.models import (
    CandidateTask,
    InstallConfig,
    SourceEvidence,
    SourceKind,
    TestEvidence,
)

__all__ = [
    "CandidateTask",
    "InstallConfig",
    "SourceEvidence",
    "SourceKind",
    "TestEvidence",
]
