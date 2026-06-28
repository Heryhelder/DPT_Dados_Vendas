# Extraction Requirements Quality Checklist: Extração de Dados CSV

**Purpose**: Validate data extraction requirements quality for pre-implementation self-check
**Created**: 2026-06-28
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [ ] CHK001 - Are the exact supported data types for inference explicitly listed (numeric, text, date — others like boolean?) [Completeness, Spec §FR-003]
- [ ] CHK002 - Is the behavior for CSV files with only a header row (zero data rows) specified? [Gap]
- [ ] CHK003 - Is the type inference fallback documented (what happens when inference fails for a column)? [Gap]

## Requirement Clarity

- [ ] CHK004 - Is the delimiter parameter constraint clear (single character only? any string?)? [Clarity, Spec §FR-004]
- [ ] CHK005 - Is whitespace handling (trimming/stripping) for column names and values explicitly specified? [Clarity, Gap]
- [ ] CHK006 - Is the behavior for BOM-prefixed CSV files clearly defined (ignore BOM, error, auto-detect)? [Clarity, Spec §Edge Cases]
- [ ] CHK007 - Are the conditions for "CSV malformado" precisely defined (any row with mismatched column count)? [Clarity, Spec §FR-009]

## Requirement Measurability

- [ ] CHK008 - Does the 100MB rejection have a verifiable acceptance scenario (e.g., Given a 101MB file)? [Measurability, Spec §FR-010]
- [ ] CHK009 - Can "colunas numéricas são reconhecidas como números" be objectively verified for edge values (negative, decimal, scientific notation)? [Measurability, Spec §US1-AS2]

## Edge Case Coverage

- [ ] CHK010 - Are requirements for handling file paths with special characters (spaces, Unicode) defined beyond just listing? [Coverage, Spec §Edge Cases]
- [ ] CHK011 - Is the row order preservation requirement documented (should rows maintain CSV order in output)? [Coverage, Gap]
- [ ] CHK012 - Is the behavior for CSV files with trailing blank lines explicitly specified (ignore, error, treat as data)? [Coverage, Spec §Edge Cases]
