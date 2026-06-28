# Extraction Requirements Quality Checklist: Extração de Dados CSV

**Purpose**: Validate data extraction requirements quality for pre-implementation self-check
**Created**: 2026-06-28
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [x] CHK001 - Are the exact supported data types for inference explicitly listed (numeric, text, date — others like boolean?) [Completeness, Spec §FR-003] ✅ FR-003 atualizado para incluir booleano
- [x] CHK002 - Is the behavior for CSV files with only a header row (zero data rows) specified? [Gap] ✅ FR-008 esclarecido: arquivo 0 bytes OU cabeçalho sem dados = erro
- [x] CHK003 - Is the type inference fallback documented (what happens when inference fails for a column)? [Gap] ✅ Decidido: não documentar — Pandas infere como string por padrão

## Requirement Clarity

- [x] CHK004 - Is the delimiter parameter constraint clear (single character only? any string?)? [Clarity, Spec §FR-004] ✅ FR-004 atualizado: apenas 1 caractere
- [x] CHK005 - Is whitespace handling (trimming/stripping) for column names and values explicitly specified? [Clarity, Gap] ✅ Trim automático documentado nas Assumptions
- [x] CHK006 - Is the behavior for BOM-prefixed CSV files clearly defined (ignore BOM, error, auto-detect)? [Clarity, Spec §Edge Cases] ✅ BOM ignorado automaticamente — documentado em FR-005
- [x] CHK007 - Are the conditions for "CSV malformado" precisely defined (any row with mismatched column count)? [Clarity, Spec §FR-009] ✅ FR-009 claro: linhas com colunas em número inconsistente

## Requirement Measurability

- [x] CHK008 - Does the 100MB rejection have a verifiable acceptance scenario (e.g., Given a 101MB file)? [Measurability, Spec §FR-010] ✅ Cenário Gherkin adicionado em US3-AS4
- [x] CHK009 - Can "colunas numéricas são reconhecidas como números" be objectively verified for edge values (negative, decimal, scientific notation)? [Measurability, Spec §US1-AS2] ✅ Golden data T005 ampliado com valores extremos

## Edge Case Coverage

- [x] CHK010 - Are requirements for handling file paths with special characters (spaces, Unicode) defined beyond just listing? [Coverage, Spec §Edge Cases] ✅ Edge Case atualizado — suportado nativamente
- [x] CHK011 - Is the row order preservation requirement documented (should rows maintain CSV order in output)? [Coverage, Gap] ✅ Decidido: não documentar — implícito no Pandas
- [x] CHK012 - Is the behavior for CSV files with trailing blank lines explicitly specified (ignore, error, treat as data)? [Coverage, Spec §Edge Cases] ✅ Linhas em branco ignoradas — documentado em Edge Cases
