# 하네스 Task Taxonomy

이 문서는 `materials-structuring`의 하네스에서 작업을 어떻게 나눌지 정리한다.

핵심 원칙은 간단하다.

- 사람 설명용 분류와 하네스 실행용 분류를 분리한다.
- 하네스는 `기획 / 분석 / 실행`보다 더 잘게 쪼갠 task type을 사용한다.
- 기본 엔진은 규칙 기반이다.
- 소형 모델은 가벼운 보조 작업에만 쓴다.
- 대형 모델은 긴 문맥, 애매한 예외, 복잡한 비교에만 쓴다.

## 1. 사람용 상위 분류

사람이 이해하기 쉽게는 아래 3가지로 설명할 수 있다.

| 상위 분류 | 의미 | 예시 |
|---|---|---|
| 기획 | 방향 정리, 요약, 설명 | 요약, 초안, 예외 설명 |
| 분석 | 문서 구조화와 판정 | 추출, 정규화, 검증, 이상탐지 |
| 실행 | 저장, 보고, 전달 | JSON 저장, CSV 저장, 리포트 생성 |

이 분류는 설명용으로는 유용하지만, 라우팅 기준으로는 너무 크다.

## 2. 하네스용 실제 Task Type

하네스는 아래처럼 더 잘게 나눈다.

| task_type | 의미 | 기본 엔진 | 비고 |
|---|---|---|---|
| `test_certificate_process` | 시험성적서 전체 처리 | `rule` | 추출~검증~출력까지 일괄 |
| `msds_process` | MSDS 전체 처리 | `rule` | 배치 검증용 |
| `extract` | 텍스트/표에서 항목 추출 | `rule` | 정규식, 표 파서 우선 |
| `normalize` | 필드명/단위 표준화 | `rule` | 사전/매핑 테이블 우선 |
| `validate` | 기준 초과, 누락, 충돌 판정 | `rule` | if 규칙 중심 |
| `report` | JSON/CSV/MD 결과물 생성 | `rule` | 포맷팅 작업 |
| `classify` | 짧은 분류 작업 | `small_model` | 애매한 항목명 분류 보조 |
| `summarize` | 짧은 요약/설명 | `small_model` | 짧은 출력 |
| `draft` | 짧은 초안 생성 | `small_model` | 내부 초안 수준 |
| `compare_multi_doc` | 여러 문서 비교 | `large_model` | 긴 문맥 비교 |
| `deep_review` | 예외 해석, 긴 설명 | `large_model` | 애매한 케이스만 |

## 3. 추천 엔진 매핑

### 규칙 기반

처음부터 규칙 기반으로 두는 작업:

- `extract`
- `normalize`
- `validate`
- `report`
- `test_certificate_process`
- `msds_process`

이 구간은 정확도와 재현성이 중요하다.

### 소형 모델

가벼운 보조 작업만 맡긴다.

- `classify`
- `summarize`
- `draft`

추천 기준:

- `GPT-5.4-mini`
- 또는 동급 소형 모델

### 대형 모델

긴 문맥이나 애매한 예외만 맡긴다.

- `compare_multi_doc`
- `deep_review`

추천 기준:

- `GPT-5.4`
- 또는 동급 상위 모델

현재 하네스 구현 기준으로는:

- `small_model_executor`는 `metadata.prompt`가 있으면 실제 OpenAI Responses API 호출이 가능하다.
- `large_model_executor`도 같은 방식으로 동작한다.
- 규칙 기반 task는 여전히 모델 호출 없이 처리한다.
- provider 구조는 [harness_provider_structure.md](/home/ubuntu/materials-structuring/docs/harness_provider_structure.md)를 따른다.

## 4. 모델 배치 기준

모델을 직접 기준으로 나누지 말고, 작업을 먼저 나눈다.

잘못된 기준:

- 단순하면 무조건 mini
- 복잡하면 무조건 large

더 좋은 기준:

1. 규칙 기반으로 가능한가
2. 짧은 보조 작업인가
3. 긴 문맥/예외 해석인가

즉:

- 규칙 가능: `rule`
- 짧은 보조: `small_model`
- 긴 문맥/애매함: `large_model`

## 5. 현재 프로젝트에 맞는 초기 기준

### 시험성적서

- `test_certificate_process` → `rule`
- `normalize` → `rule`
- `validate` → `rule`
- `summarize` → `small_model` (나중)
- `deep_review` → `large_model` (나중)

### MSDS

- `msds_process` → `rule`
- `normalize` → `rule`
- `validate` → `rule`
- `summarize` → `small_model` (나중)

## 6. 한 줄 결론

사람 설명은 `기획 / 분석 / 실행`으로 해도 되지만, 하네스는 `추출 / 정규화 / 검증 / 보고 / 요약 / 심화검토` 같은 실제 task type으로 나누는 쪽이 더 안정적이다.
