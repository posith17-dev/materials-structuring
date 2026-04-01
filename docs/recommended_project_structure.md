# 권장 디렉토리 구조

이 문서는 `materials-structuring` 안에서 규칙 기반, 로컬 모델, 문서군 확장을 같이 가져갈 때의 권장 구조를 정리한다.

## 1. 기본 원칙

- 공통 코어와 문서군별 코드를 분리한다.
- 규칙 기반과 모델 보조층을 분리한다.
- 입력 샘플, 결과물, 문서를 서로 섞지 않는다.
- 회사별 차이는 코드가 아니라 설정 파일로 먼저 분리한다.

## 2. 권장 트리

```text
materials-structuring/
  README.md
  docs/
    ...
    recommended_project_structure.md
  prompts/
    ...
  samples/
    msds_batch/
    msds_bromotoluene_batch/
    test_certificate_batch/
  outputs/
    ...
  storage/
    ...
  src/
    common/
      parser.py
      text_utils.py
      schema.py
      harness/
        router.py
        policy.py
        schemas.py
        executors/
          rule_executor.py
          small_model_executor.py
          large_model_executor.py
    msds/
      extractor.py
      validator.py
      reporter.py
      main.py
    test_certificate/
      parser.py
      extractor.py
      normalizer.py
      validator.py
      reporter.py
      main.py
    patent/
      ...
  config/
    profiles/
      company_a.yaml
      company_b.yaml
    rules/
      msds_rules.yaml
      test_certificate_rules.yaml
  scripts/
    run_msds_batch_validate.py
    run_test_certificate_mvp.py
    run_openai_material_extraction.py
```

## 3. 폴더 역할

### `src/common/`

공통으로 재사용하는 코드만 둔다.

- PDF/텍스트 추출 보조
- 공통 정규화
- 공통 스키마
- 공통 유틸
- 공통 하네스/오케스트레이션

### `src/common/harness/`

작업을 적절한 엔진으로 보내는 공통 오케스트레이션 계층이다.

- `router.py`
  - 작업 유형을 분류한다.
- `policy.py`
  - 비용, 보안, fallback 규칙을 결정한다.
- `schemas.py`
  - task/result 공통 구조를 정의한다.
- `executors/`
  - 규칙 기반, 소형 모델, 대형 모델 실행기를 분리한다.

하네스는 문서군 전용이 아니라 공통 계층으로 둔다.
처음에는 규칙 기반 executor만 실제로 써도 되고, 모델 executor는 나중에 붙여도 된다.

### `src/<domain>/`

문서군별 구현을 둔다.

- `msds/`
- `test_certificate/`
- `patent/`

도메인별 차이가 있는 규칙, 파서, 리포트는 여기에 둔다.

### 현재 코드와의 매핑

- 현재 구현된 시험성적서 초안은 `src/test_certificate_mvp/`에 있다.
- 장기적으로는 `src/test_certificate/`로 이름을 맞추는 편이 더 깔끔하다.
- MSDS도 동일한 방식으로 `src/msds/`로 맞추면 된다.

### `config/`

회사별 요구사항과 규칙을 코드 밖으로 뺀다.

- 기준값
- 제외 규칙
- 단위 매핑
- 알림 방식
- 리포트 포맷 차이

### `samples/`

검증용 입력만 둔다.

- PDF
- HTML
- TXT
- 테스트 배치 폴더

### `outputs/`

실행 결과만 둔다.

- JSON
- CSV
- MD 리포트
- 검증 리포트

## 4. 확장 규칙

- 새 문서군이 생기면 `src/<new_domain>/`를 추가한다.
- 공통 로직이 늘어나면 `src/common/`으로 올린다.
- 작업 라우팅이 필요해지면 `src/common/harness/`에 추가한다.
- task type 기준은 [harness_task_taxonomy.md](/home/ubuntu/materials-structuring/docs/harness_task_taxonomy.md)를 따른다.
- 회사별 차이는 먼저 `config/`로 처리한다.
- 로컬 모델은 설명/요약층으로만 붙인다.
- 클라우드는 예외 fallback으로만 붙인다.

## 5. 피해야 할 구조

- 문서군별로 파일을 여기저기 흩뿌리는 구조
- 규칙 기반과 LLM이 한 파일에 섞인 구조
- 회사별 차이를 코드 if문으로만 끝내는 구조
- `samples/`와 `outputs/`를 운영 데이터로 섞는 구조

## 6. 한 줄 결론

공통 코어는 `src/common/`, 하네스는 `src/common/harness/`, 문서군별 구현은 `src/<domain>/`, 회사별 차이는 `config/`로 나누는 구조가 가장 오래 간다.
