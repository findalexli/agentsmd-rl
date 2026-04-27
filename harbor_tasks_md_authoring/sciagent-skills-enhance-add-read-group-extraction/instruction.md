# Enhance: Add read group extraction documentation to pysam skill

Source: [jaechang-hits/SciAgent-Skills#9](https://github.com/jaechang-hits/SciAgent-Skills/pull/9)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md`

## What to add / change

## Summary

Addresses GitHub issue #8 by enhancing the existing pysam-genomic-files skill with comprehensive read group handling documentation.

### What's Added

- **New Section 5: Read Groups and Sample Information** with practical code examples:
  - Access and list read groups from BAM headers
  - Extract reads from specific read group IDs
  - Count reads per sample with RG-to-sample mapping
  
- **Enhanced Key Concepts** table explaining RG tag structure (ID, SM, LB, PL fields)

- **Improved Troubleshooting** section with read group debugging tips

### Coverage of Issue #8 Requirements

✅ Reading alignments from BAM/SAM/CRAM files (already covered, enhanced)  
✅ Filtering by region, quality scores, and flags (already covered, enhanced)  
✅ Computing coverage and depth metrics (already covered, enhanced)  
✅ **Extracting read group information** (NEW - fully documented)  
✅ Indexing operations (already covered, enhanced)  

### Code Examples

- : Filter multi-sample BAM by read group
- : Count alignment statistics per sample
- Header inspection methods for read group validation

All examples are production-ready and follow pysam best practices.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
