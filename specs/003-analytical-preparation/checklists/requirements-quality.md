# Requirements Quality Checklist: Analytical Data Preparation

**Purpose**: Unit tests for requirements — validate quality, clarity, and completeness of spec writing
**Created**: 2026-07-12
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [ ] CHK001 - Are error handling requirements defined for when `validate_sales` output has unexpected columns? [Gap, Spec §FR-001 to FR-013]
- [x] CHK002 - Are requirements specified for what happens when the input DataFrame has more than 25 columns? [Gap] — FR-012: "return new DataFrame with all existing columns preserved" implies extra columns pass through
- [x] CHK003 - Are requirements defined for the exact data types of output columns (month, year, quarter — int vs float)? [Clarity, Spec §FR-001 to FR-003] — FR-001–FR-003 specify float64; clarification confirms
- [ ] CHK004 - Are requirements documented for column ordering in the output DataFrame? [Gap] — Contract specifies "time columns appended after original columns" but spec does not
- [ ] CHK005 - Are requirements specified for the function's behavior when called multiple times on the same input? [Completeness, Spec §FR-012] — Implied safe by immutability, not explicit

## Requirement Clarity

- [ ] CHK006 - Is "title case" precisely defined for strings with accents, apostrophes, or hyphens (e.g., "São Paulo", "O'Brien")? [Clarity, Spec §FR-005 to FR-009] — Edge case line 71 says "preserved as-is" but doesn't define `.str.title()` behavior with accents
- [x] CHK007 - Is "gracefully" in FR-011 quantified with specific behavior (preserve as NaN, skip, or log warning)? [Clarity, Spec §FR-011] — FR-011 now says "preserve NaN/None" — explicitly quantified
- [ ] CHK008 - Is "various formats" in acceptance scenario US1.4 enumerated or bounded with examples? [Clarity, Spec §US1 Scenario 4] — Still unbounded
- [ ] CHK009 - Is "meaningful" in US3.4 acceptance scenario defined with measurable criteria? [Clarity, Spec §US3 Scenario 4] — Still undefined
- [ ] CHK010 - Is the term "standardize" in FR-005 through FR-009 distinguished from the existing `_clean_text` standardization in `validate.py`? [Clarity, Spec §FR-005] — Not distinguished in spec

## Requirement Consistency

- [x] CHK011 - Are the 5 dimension columns in FR-005 to FR-009 consistent with the DIMENSION_COLUMNS list defined in the Clarifications section? [Consistency, Spec §FR-005 to FR-009 vs §Clarifications] — 5 columns match between FR-005–FR-009 and Key Entities section
- [x] CHK012 - Does FR-010 (NULL date handling) align with the Edge Cases section's "set to NULL" behavior? [Consistency, Spec §FR-010 vs §Edge Cases] — Both now say NaN — consistent
- [x] CHK013 - Are the time column names (month, year, quarter) consistent between FR-001 to FR-003 and SC-001? [Consistency, Spec §FR-001 to FR-003 vs §SC-001] — "month", "year", "quarter" consistent across FR and SC-001
- [x] CHK014 - Does FR-013 logging requirement align with the specific statistics listed in the Clarifications session? [Consistency, Spec §FR-013 vs §Clarifications] — FR-013 stats match Clarifications session

## Acceptance Criteria Quality

- [x] CHK015 - Can SC-001 ("under 1 second for 100,000 rows") be objectively measured without implementation details? [Measurability, Spec §SC-001] — Yes, "under 1 second for 100K rows" is objectively measurable
- [ ] CHK016 - Can SC-002 ("100% identical values for identical underlying data") be verified independently of implementation? [Measurability, Spec §SC-002] — Requires implementation to verify
- [ ] CHK017 - Are success criteria SC-003 to SC-004 (filtering, cross-dimensional analysis) measurable without running code? [Measurability, Spec §SC-003 to SC-004] — Requires code execution to verify
- [ ] CHK018 - Is SC-006 ("deterministic") defined with a specific test method (e.g., run twice, compare output)? [Measurability, Spec §SC-006] — No test method specified

## Scenario Coverage

- [ ] CHK019 - Are requirements defined for the scenario where `order_date` is a valid datetime but in a timezone-aware format? [Coverage, Gap] — Not addressed
- [ ] CHK020 - Are requirements specified for what happens when dimension columns contain numeric values instead of strings? [Coverage, Gap] — Assumption says "valid values" but no requirement for numeric-in-dimension
- [ ] CHK021 - Are requirements documented for the scenario where the input DataFrame has duplicate column names? [Coverage, Gap] — Not addressed
- [ ] CHK022 - Are requirements defined for concurrent calls to `prepare_sales` on shared DataFrames? [Coverage, Gap] — Implied safe by immutability, not explicit
- [ ] CHK023 - Are recovery/rollback requirements specified if the preparation fails mid-execution? [Coverage, Gap] — Not addressed

## Edge Case Coverage

- [ ] CHK024 - Are requirements defined for handling of extremely large year values (e.g., year 9999)? [Edge Case, Gap] — Not addressed
- [ ] CHK025 - Are requirements specified for what happens when `order_date` contains NaT (Not a Time) vs NULL? [Edge Case, Gap] — NaT vs NULL distinction not explicit
- [ ] CHK026 - Are requirements documented for dimension columns with only whitespace (e.g., "   ")? [Edge Case, Gap] — Not addressed (contract applies strip, but spec doesn't define behavior)
- [ ] CHK027 - Are requirements defined for the scenario where all rows have NULL `order_date`? [Edge Case, Gap] — Implied by FR-010, not explicitly addressed

## Non-Functional Requirements

- [ ] CHK028 - Are memory usage requirements specified for processing 100,000 rows? [Gap, NFR] — Not addressed
- [ ] CHK029 - Are requirements documented for the maximum number of unique dimension values the system must handle? [Gap, NFR] — Not addressed
- [ ] CHK030 - Are logging format requirements specified (structured vs plain text, severity levels)? [Gap, Spec §FR-013] — Structured logging in research.md, not in spec

## Dependencies & Assumptions

- [x] CHK031 - Is the assumption "Input data has already been validated" validated against the actual `validate_sales` output contract? [Assumption, Spec §Assumptions] — Contract confirms input requirements match validate_sales output
- [ ] CHK032 - Are requirements documented for what happens if `prepare_sales` is called before `validate_sales` in the pipeline? [Dependency, Gap] — Contract has AttributeError, spec doesn't address ordering
- [ ] CHK033 - Is the dependency on pandas `dt.quarter` behavior documented (calendar year only)? [Dependency, Spec §FR-003] — Calendar year in FR-003, but pandas dt.quarter dependency not explicit in spec

## Ambiguities & Conflicts

- [ ] CHK034 - Is there ambiguity in whether "standardize" in FR-005 to FR-009 means the same operation as `_clean_text` in `validate.py`? [Ambiguity, Spec §FR-005] — Not distinguished
- [x] CHK035 - Is there a conflict between FR-004 ("preserve order_date unchanged") and the need to convert order_date to datetime for time extraction? [Conflict, Spec §FR-004 vs §FR-001] — No conflict: FR-004 preserves column, FR-001 extracts from it (pandas dt accessor doesn't modify)
- [x] CHK036 - Are the 3 new columns (month, year, quarter) required to be float64 (to support NaN) or int64 (for cleaner output)? [Ambiguity, Spec §FR-001 to FR-003] — float64 explicitly in FR-001–FR-003 + clarification
