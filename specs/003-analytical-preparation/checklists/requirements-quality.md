# Requirements Quality Checklist: Analytical Data Preparation

**Purpose**: Unit tests for requirements — validate quality, clarity, and completeness of spec writing
**Created**: 2026-07-12
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [ ] CHK001 - Are error handling requirements defined for when `validate_sales` output has unexpected columns? [Gap, Spec §FR-001 to FR-013]
- [ ] CHK002 - Are requirements specified for what happens when the input DataFrame has more than 25 columns? [Gap]
- [ ] CHK003 - Are requirements defined for the exact data types of output columns (month, year, quarter — int vs float)? [Clarity, Spec §FR-001 to FR-003]
- [ ] CHK004 - Are requirements documented for column ordering in the output DataFrame? [Gap]
- [ ] CHK005 - Are requirements specified for the function's behavior when called multiple times on the same input? [Completeness, Spec §FR-012]

## Requirement Clarity

- [ ] CHK006 - Is "title case" precisely defined for strings with accents, apostrophes, or hyphens (e.g., "São Paulo", "O'Brien")? [Clarity, Spec §FR-005 to FR-009]
- [ ] CHK007 - Is "gracefully" in FR-011 quantified with specific behavior (preserve as NaN, skip, or log warning)? [Clarity, Spec §FR-011]
- [ ] CHK008 - Is "various formats" in acceptance scenario US1.4 enumerated or bounded with examples? [Clarity, Spec §US1 Scenario 4]
- [ ] CHK009 - Is "meaningful" in US3.4 acceptance scenario defined with measurable criteria? [Clarity, Spec §US3 Scenario 4]
- [ ] CHK010 - Is the term "standardize" in FR-005 through FR-009 distinguished from the existing `_clean_text` standardization in `validate.py`? [Clarity, Spec §FR-005]

## Requirement Consistency

- [ ] CHK011 - Are the 5 dimension columns in FR-005 to FR-009 consistent with the DIMENSION_COLUMNS list defined in the Clarifications section? [Consistency, Spec §FR-005 to FR-009 vs §Clarifications]
- [ ] CHK012 - Does FR-010 (NULL date handling) align with the Edge Cases section's "set to NULL" behavior? [Consistency, Spec §FR-010 vs §Edge Cases]
- [ ] CHK013 - Are the time column names (month, year, quarter) consistent between FR-001 to FR-003 and SC-001? [Consistency, Spec §FR-001 to FR-003 vs §SC-001]
- [ ] CHK014 - Does FR-013 logging requirement align with the specific statistics listed in the Clarifications session? [Consistency, Spec §FR-013 vs §Clarifications]

## Acceptance Criteria Quality

- [ ] CHK015 - Can SC-001 ("under 1 second for 100,000 rows") be objectively measured without implementation details? [Measurability, Spec §SC-001]
- [ ] CHK016 - Can SC-002 ("100% identical values for identical underlying data") be verified independently of implementation? [Measurability, Spec §SC-002]
- [ ] CHK017 - Are success criteria SC-003 to SC-004 (filtering, cross-dimensional analysis) measurable without running code? [Measurability, Spec §SC-003 to SC-004]
- [ ] CHK018 - Is SC-006 ("deterministic") defined with a specific test method (e.g., run twice, compare output)? [Measurability, Spec §SC-006]

## Scenario Coverage

- [ ] CHK019 - Are requirements defined for the scenario where `order_date` is a valid datetime but in a timezone-aware format? [Coverage, Gap]
- [ ] CHK020 - Are requirements specified for what happens when dimension columns contain numeric values instead of strings? [Coverage, Gap]
- [ ] CHK021 - Are requirements documented for the scenario where the input DataFrame has duplicate column names? [Coverage, Gap]
- [ ] CHK022 - Are requirements defined for concurrent calls to `prepare_sales` on shared DataFrames? [Coverage, Gap]
- [ ] CHK023 - Are recovery/rollback requirements specified if the preparation fails mid-execution? [Coverage, Gap]

## Edge Case Coverage

- [ ] CHK024 - Are requirements defined for handling of extremely large year values (e.g., year 9999)? [Edge Case, Gap]
- [ ] CHK025 - Are requirements specified for what happens when `order_date` contains NaT (Not a Time) vs NULL? [Edge Case, Gap]
- [ ] CHK026 - Are requirements documented for dimension columns with only whitespace (e.g., "   ")? [Edge Case, Gap]
- [ ] CHK027 - Are requirements defined for the scenario where all rows have NULL `order_date`? [Edge Case, Gap]

## Non-Functional Requirements

- [ ] CHK028 - Are memory usage requirements specified for processing 100,000 rows? [Gap, NFR]
- [ ] CHK029 - Are requirements documented for the maximum number of unique dimension values the system must handle? [Gap, NFR]
- [ ] CHK030 - Are logging format requirements specified (structured vs plain text, severity levels)? [Gap, Spec §FR-013]

## Dependencies & Assumptions

- [ ] CHK031 - Is the assumption "Input data has already been validated" validated against the actual `validate_sales` output contract? [Assumption, Spec §Assumptions]
- [ ] CHK032 - Are requirements documented for what happens if `prepare_sales` is called before `validate_sales` in the pipeline? [Dependency, Gap]
- [ ] CHK033 - Is the dependency on pandas `dt.quarter` behavior documented (calendar year only)? [Dependency, Spec §FR-003]

## Ambiguities & Conflicts

- [ ] CHK034 - Is there ambiguity in whether "standardize" in FR-005 to FR-009 means the same operation as `_clean_text` in `validate.py`? [Ambiguity, Spec §FR-005]
- [ ] CHK035 - Is there a conflict between FR-004 ("preserve order_date unchanged") and the need to convert order_date to datetime for time extraction? [Conflict, Spec §FR-004 vs §FR-001]
- [ ] CHK036 - Are the 3 new columns (month, year, quarter) required to be float64 (to support NaN) or int64 (for cleaner output)? [Ambiguity, Spec §FR-001 to FR-003]
