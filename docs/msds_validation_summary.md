# MSDS Validation Summary

## What was validated

- A single MSDS material was validated in two input formats:
  - HTML
  - TXT
- Material:
  - 도데칸니트릴
  - CAS No. 2437-25-4

## What worked

- `reader -> inspect -> report` pipeline ran successfully.
- HTML and TXT both produced the same material identity.
- Batch validation report was generated successfully.
- Core fields were extracted and normalized.

## Extracted core fields

- product_name
- CAS No
- composition
- composition_ratio
- exposure_limit_domestic
- exposure_limit_acgih
- exposure_limit_other
- physical_state
- color
- melting_point
- boiling_point_range
- flash_point
- vapor_pressure
- solubility
- specific_gravity

## Reliability notes

- File naming was standardized to `msds_{product_slug}_{cas_no}.{ext}`.
- File content and file name were aligned.
- HTML and TXT were cross-checked to represent the same material.
- The validation is trustworthy only when source material identity matches across formats.

## What this means for the product

- The pipeline can turn MSDS documents into structured data.
- The same structure can be reused for related industrial documents.
- The key product value is reducing manual retyping and making document data searchable.

## Current scope

- This is a validation baseline, not a full production rollout.
- Field coverage and input variety can be expanded later if needed.

