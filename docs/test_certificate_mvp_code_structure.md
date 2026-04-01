# 시험성적서 MVP 코드 구조

이 문서는 규칙 기반 시험성적서 MVP의 실제 코드 초안 구조를 정리한다.

## 패키지 구조

```text
src/common/harness/
  router.py
  policy.py
  schemas.py
  cli.py
  executors/
    rule_executor.py
    small_model_executor.py
    large_model_executor.py

src/test_certificate/
  __init__.py
  models.py
  parser.py
  extractor.py
  normalizer.py
  validator.py
  reporter.py
  main.py
```

## 역할

- `src/common/harness/router.py`
  - 작업 종류를 나누고 실행 경로를 결정한다.
- `src/common/harness/policy.py`
  - 규칙 기반 우선, 모델 fallback 같은 공통 정책을 둔다.
- `src/common/harness/cli.py`
  - 문서군별 공통 진입점이다.
- `src/common/harness/executors/rule_executor.py`
  - 규칙 기반 작업 실행을 감싼다.

- `models.py`
  - 공통 데이터 구조를 정의한다.
- `parser.py`
  - PDF, TXT, MD에서 텍스트를 읽는다.
- `extractor.py`
  - 날짜, 품목명, 로트번호, 시험 항목을 규칙으로 뽑는다.
- `normalizer.py`
  - 필드명과 단위를 표준화한다.
- `validator.py`
  - 기준 초과, 누락, 충돌을 규칙으로 판정한다.
- `reporter.py`
  - JSON, CSV, MD 결과물을 만든다.
- `main.py`
  - 전체 파이프라인을 실행하는 CLI 진입점이다.

## 실행 순서

```text
입력 파일
→ 텍스트 추출
→ 메타데이터 추출
→ 레코드 추출
→ 정규화
→ 이상탐지
→ JSON/CSV/MD 저장
```

## 설계 원칙

- 규칙 기반을 코어로 둔다.
- LLM은 이 단계에서 넣지 않는다.
- 하네스가 생겨도 첫 실행기는 규칙 기반으로 둔다.
- 문서 포맷이 조금 달라도 공통 스키마를 우선 맞춘다.
- 결과는 사람이 확인 가능한 수준으로 남긴다.

## 현재 상태

- 현재 구현은 `src/test_certificate/`에 둔다.
- 문서명은 MVP 초안이지만, 폴더명은 최종 구조 기준으로 맞췄다.
- 하네스 계층이 필요해지면 `src/common/harness/`를 추가하고, 시험성적서 코드는 그대로 유지한다.
- 공통 실행은 `scripts/run_harness.py --document-type test_certificate --input ... --output-dir ...` 형태로 시작할 수 있다.
