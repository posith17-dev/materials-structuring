# materials-structuring

소재/과학 문서에서 구조화 데이터를 추출하는 실험용 프로젝트입니다.

현재 목표는 "기초과학"이 아니라 **과학 데이터 구조화**입니다.

핵심 기술 축:
- PDF/HTML 파싱
- 표/문단 추출
- LLM 기반 정보 추출
- 정규화 스키마 적재
- 사람이 빠르게 검수 가능한 출력

## 현재 우선순위

1. 논문 PDF 1편에서 물성 추출 실험
2. 최소 스키마로 JSON/CSV 구조화
3. 사람이 5분 안에 검수 가능한지 확인

사업화/장기 확장은 나중 문제로 두고, 먼저 **"진짜로 뽑히는가"**를 확인합니다.

## 폴더 구조

```text
/home/ubuntu/materials-structuring/
├── README.md
├── .gitignore
├── docs/
├── prompts/
├── samples/
├── scripts/
└── outputs/
```

## 첫 실험 후보

- 논문 PDF 물성 추출
  - 소재명
  - 조성
  - 물성명
  - 값
  - 단위
  - 실험 조건

실험 스크립트:

```bash
python3 /home/ubuntu/materials-structuring/scripts/material_property_experiment.py \
  --input /home/ubuntu/materials-structuring/samples/paper.pdf \
  --output /home/ubuntu/materials-structuring/outputs/material_property_experiment.json
```

주의:
- PDF는 `pypdf`가 설치돼 있어야 텍스트 추출이 됩니다.
- PDF가 막히는 소스는 HTML 본문으로도 같은 스크립트를 돌릴 수 있습니다.
- 지금은 LLM 호출까지 자동화하지 않고, 추출용 JSON 스텁을 만드는 단계입니다.
- 실험 JSON에는 `candidate_segments` / `candidate_text`가 같이 들어가며, 숫자+단위+물성 키워드가 있는 구간을 우선 추립니다.
- `candidate_segment_details`에는 각 후보 구간의 `score`, `matched_units`, `matched_keywords`, `flags`가 함께 저장됩니다.

LLM 입력 번들 생성:

```bash
python3 /home/ubuntu/materials-structuring/scripts/build_llm_extraction_input.py \
  --experiment /home/ubuntu/materials-structuring/outputs/material_property_experiment.json \
  --output /home/ubuntu/materials-structuring/outputs/material_property_prompt_bundle.json
```

메모:
- `build_llm_extraction_input.py`는 기본적으로 `candidate_text`를 우선 사용합니다.
- 즉 문서 전체 `text_preview`보다 값이 있는 문단을 먼저 LLM에 보냅니다.

문서군별 프롬프트 선택 예:

```bash
python3 /home/ubuntu/materials-structuring/scripts/build_llm_extraction_input.py \
  --experiment /home/ubuntu/materials-structuring/outputs/WO2013162658A2_experiment.json \
  --document-kind patent \
  --output /home/ubuntu/materials-structuring/outputs/WO2013162658A2_patent_prompt_bundle.json
```

LLM 결과 병합:

```bash
python3 /home/ubuntu/materials-structuring/scripts/merge_llm_extraction_output.py \
  --experiment /home/ubuntu/materials-structuring/outputs/material_property_experiment.json \
  --llm-output /home/ubuntu/materials-structuring/outputs/llm_records.json \
  --output /home/ubuntu/materials-structuring/outputs/material_property_experiment_merged.json
```

LLM 결과 검증:

```bash
python3 /home/ubuntu/materials-structuring/scripts/validate_llm_extraction_output.py \
  --input /home/ubuntu/materials-structuring/outputs/llm_records.json
```

수동 검수 CLI:

```bash
python3 /home/ubuntu/materials-structuring/scripts/review_extraction_records.py \
  --input /home/ubuntu/materials-structuring/outputs/llm_records.json \
  --output /home/ubuntu/materials-structuring/outputs/llm_records_reviewed.json
```

검수 반영 병합:

```bash
python3 /home/ubuntu/materials-structuring/scripts/merge_reviewed_records.py \
  --experiment /home/ubuntu/materials-structuring/outputs/material_property_experiment.json \
  --review /home/ubuntu/materials-structuring/outputs/llm_records_reviewed.json \
  --output /home/ubuntu/materials-structuring/outputs/material_property_experiment_reviewed.json
```

검수 완료 결과를 정규화/DB 적재:

```bash
python3 /home/ubuntu/materials-structuring/scripts/process_reviewed_experiments.py \
  --input /home/ubuntu/materials-structuring/outputs/material_property_experiment_reviewed.json \
  --normalized-output /home/ubuntu/materials-structuring/outputs/reviewed_normalized_documents.json \
  --jsonl-output /home/ubuntu/materials-structuring/outputs/reviewed_normalized_records.jsonl \
  --db /home/ubuntu/materials-structuring/storage/materials_reviewed.duckdb
```

검수 품질 리포트:

```bash
python3 /home/ubuntu/materials-structuring/scripts/report_review_quality.py \
  --reviews /home/ubuntu/materials-structuring/outputs/llm_records_reviewed.json \
  --output /home/ubuntu/materials-structuring/outputs/review_quality_report.json \
  --raw-db /home/ubuntu/materials-structuring/storage/materials.duckdb \
  --reviewed-db /home/ubuntu/materials-structuring/storage/materials_reviewed.duckdb
```

OpenAI 자동 추출 실행:

```bash
python3 /home/ubuntu/materials-structuring/scripts/run_openai_material_extraction.py \
  --experiment /home/ubuntu/materials-structuring/outputs/PMC8953245_experiment.json \
  --llm-output /home/ubuntu/materials-structuring/outputs/PMC8953245_openai_records.json \
  --merged-output /home/ubuntu/materials-structuring/outputs/PMC8953245_openai_merged.json
```

COA 문서 예:

```bash
python3 /home/ubuntu/materials-structuring/scripts/run_openai_material_extraction.py \
  --experiment /home/ubuntu/materials-structuring/outputs/ti6al4v_coa_experiment.json \
  --document-kind coa \
  --llm-output /home/ubuntu/materials-structuring/outputs/ti6al4v_coa_openai_records.json \
  --merged-output /home/ubuntu/materials-structuring/outputs/ti6al4v_coa_openai_merged.json
```

메모:
- `OPENAI_API_KEY`는 환경변수나 `/home/ubuntu/trading-system/config/secrets.env`에서 읽습니다.
- 모델은 `OPENAI_MODEL`을 우선 사용하고, 없으면 `gpt-4o-mini`를 기본값으로 사용합니다.

## 이후 확장 후보

- 특허에서 조성 추출
- 시험성적서/COA/사양서 구조화
- 연구실 시뮬레이션 결과 정규화

## 특허 실험 메모

- 논문뿐 아니라 공개 특허 본문도 같은 흐름으로 다룰 수 있습니다.
- 현재 샘플:
  - [WO2013162658A2 특허 발췌 샘플](/home/ubuntu/materials-structuring/samples/WO2013162658A2_patent_excerpt.html)
  - [WO2013162658A2 구조화 결과](/home/ubuntu/materials-structuring/outputs/WO2013162658A2_material_properties.md)
  - [US9956629B2 특허 본문 샘플](/home/ubuntu/materials-structuring/samples/US9956629B2_patent_body_sample.html)
  - [US9956629B2 구조화 결과](/home/ubuntu/materials-structuring/outputs/US9956629B2_material_properties.md)
- 특허 전용 프롬프트:
  - [patent_composition_extraction_prompt.md](/home/ubuntu/materials-structuring/prompts/patent_composition_extraction_prompt.md)

## COA/성적서 실험 메모

- 시험성적서/COA도 같은 구조로 처리할 수 있습니다.
- 현재 샘플:
  - [ti6al4v_coa_sample.html](/home/ubuntu/materials-structuring/samples/ti6al4v_coa_sample.html)
  - [ti6al4v_coa_material_properties.md](/home/ubuntu/materials-structuring/outputs/ti6al4v_coa_material_properties.md)
- COA 전용 프롬프트:
  - [coa_property_extraction_prompt.md](/home/ubuntu/materials-structuring/prompts/coa_property_extraction_prompt.md)

## 운영 원칙

- 화려한 장기 계획보다 작은 추출 실험을 먼저 한다
- PDF 1개에서 10개 필드를 뽑는 것부터 시작한다
- 출력은 반드시 구조화 JSON/CSV로 남긴다
- 검수 가능한 수준인지 먼저 보고, 그다음 자동화를 늘린다

## 정규화

- 문서군별 결과는 공통 코어 스키마로 다시 맞춥니다.
- 스키마 문서:
  - [normalized_schema.md](/home/ubuntu/materials-structuring/docs/normalized_schema.md)
- 정규화 스크립트:

```bash
python3 /home/ubuntu/materials-structuring/scripts/normalize_material_records.py \
  --input \
    /home/ubuntu/materials-structuring/outputs/PMC5109614_material_properties.json \
    /home/ubuntu/materials-structuring/outputs/PMC8953245_material_properties.json \
  --output /home/ubuntu/materials-structuring/outputs/normalized_documents.json \
  --jsonl-output /home/ubuntu/materials-structuring/outputs/normalized_records.jsonl
```

## DuckDB 적재/조회

적재:

```bash
python3 /home/ubuntu/materials-structuring/scripts/load_normalized_to_duckdb.py \
  --input /home/ubuntu/materials-structuring/outputs/normalized_documents.json \
  --db /home/ubuntu/materials-structuring/storage/materials.duckdb
```

조회:

```bash
python3 /home/ubuntu/materials-structuring/scripts/query_material_records.py \
  --db /home/ubuntu/materials-structuring/storage/materials.duckdb \
  --material Ti-6Al-4V \
  --property 인장강도
```

정규화된 속성명 기준 조회:

```bash
python3 /home/ubuntu/materials-structuring/scripts/query_material_records.py \
  --db /home/ubuntu/materials-structuring/storage/materials.duckdb \
  --material Ti-6Al-4V \
  --canonical-property ultimate_tensile_strength
```

소재별 속성 요약:

```bash
python3 /home/ubuntu/materials-structuring/scripts/summarize_material_records.py \
  --db /home/ubuntu/materials-structuring/storage/materials.duckdb \
  --material Ti-6Al-4V
```
