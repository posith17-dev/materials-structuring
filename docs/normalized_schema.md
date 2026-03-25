# Normalized Schema

문서군이 달라도 아래 공통 스키마로 맞춘 뒤 저장/검색/DB 적재를 진행합니다.

## Document-level fields

- `source_file`: 원본 입력 파일 경로
- `document_type`: `paper` | `patent` | `certificate_of_analysis`
- `document_title`: 논문/특허/성적서 제목
- `document_id`: 문서 식별자
  - 예: `PMC5109614`, `US9956629B2`, `coa:ti6al4v_coa_sample`

## Record-level fields

- `material_name_or_composition`
- `property_name`
- `property_value`
- `property_unit`
- `test_condition`
- `source_ref`
- `source_file`
- `document_type`
- `document_title`
- `document_id`

## 원칙

1. 문서군별 추가 메타는 유지하되, 검색/DB의 기본 적재는 위 공통 필드로 맞춘다.
2. `test_condition`은 원문에 없으면 빈 문자열로 둔다.
3. `source_ref`는 `Table 1`, `Figure 3`, `본문` 같은 짧은 출처 문자열이다.
4. 값/단위는 원문 표기를 최대한 유지한다.
5. 조성도 물성처럼 개별 레코드로 저장할 수 있다.
