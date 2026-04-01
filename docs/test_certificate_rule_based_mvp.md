# 시험성적서 규칙 기반 구조화·이상탐지 MVP 설계 문서

## 1. 문제 정의

시험성적서를 처리할 때 현장에서 사람이 하는 일은 거의 비슷하다.

- PDF를 연다.
- 시험 항목을 찾는다.
- 항목명, 측정값, 단위를 읽는다.
- 규격 하한/상한을 확인한다.
- 기준 초과, 미달, 누락이 있는지 본다.
- 결과를 엑셀에 옮기거나 리포트에 적는다.

이 작업은 반복적이다.

- 문서 포맷이 회사마다 다르다.
- 같은 문서군인데도 표 구조가 다르다.
- 항목명 표기가 조금씩 다르다.
- 수치와 단위가 섞여 있다.
- 사람이 매번 다시 확인해야 한다.

자동화 가치가 있는 이유는 분명하다.

- 수작업 시간을 줄일 수 있다.
- 누락과 단위 오류를 줄일 수 있다.
- 기준 초과/미달을 일관되게 볼 수 있다.
- 엑셀 복사 붙여넣기 작업을 줄일 수 있다.

이 MVP가 해결하려는 범위는 좁게 잡는다.

- 시험성적서 PDF 10~20개
- 텍스트 기반 문서 중심
- 표와 수치가 있는 문서 중심
- 규칙 기반 구조화와 이상탐지

해결하지 않을 범위도 분명히 둔다.

- 자유서술 해석
- 다양한 회사 포맷의 완전 일반화
- 로컬 LLM 자연어 설명
- 클라우드 AI 연동
- 대시보드/웹 UI

## 2. MVP 목표

| 항목     | 정의 |
|----------|------|
| 입력     | 시험성적서 PDF 1건 |
| 처리     | 표/텍스트 추출, 필드 구조화, 이상탐지 |
| 출력     | JSON + CSV + 간단 리포트 |
| 성공 기준 | 주요 필드 정확 추출, 기준 초과/미달/누락 탐지 가능 |

성공 기준은 실무 기준으로 본다.

- 사람이 다시 읽어야 하는 항목 수가 줄어야 한다.
- 문서 1건 처리 시간이 줄어야 한다.
- 규칙이 반복 문서에 대해 안정적으로 돌아야 한다.

## 3. 공통 스키마 정의

공통 스키마는 강제로 고정한다.

| 필드명        | 의미                         | 자료형   | 필수 여부 | 추출 난이도 |
|---------------|------------------------------|----------|-----------|-------------|
| document_name | 문서명                       | string   | 필수      | 낮음        |
| issue_date    | 발행일 또는 검사일           | string   | 필수      | 중간        |
| product_name  | 제품명                       | string   | 필수      | 낮음        |
| lot_no        | 로트번호 또는 Batch No.      | string   | 선택      | 중간        |
| item_name     | 시험 항목명                  | string   | 필수      | 중간        |
| measured_value| 측정값                       | number   | 필수      | 중간        |
| unit          | 단위                         | string   | 필수      | 중간        |
| lower_spec    | 규격 하한                    | number   | 선택      | 중간        |
| upper_spec    | 규격 상한                    | number   | 선택      | 중간        |
| judgment      | 판정(PASS/FAIL/NA)           | string   | 필수      | 낮음        |
| source_page   | 출처 페이지                  | number   | 선택      | 낮음        |
| raw_text      | 원문 일부                    | string   | 필수      | 낮음        |

스키마 원칙:

- 값이 없으면 빈 문자열이나 `null`로 남긴다.
- 숫자는 숫자로 저장한다.
- 추출값과 원문 출처를 같이 남긴다.
- 문서별 추가 필드는 별도 메타로 두되, 기본 적재는 이 공통 스키마를 따른다.

## 4. 입력 문서 특성 가정

초기 MVP에서 가정하는 문서는 다음과 같다.

- 텍스트 기반 PDF가 대부분이다.
- 스캔 PDF는 일부만 포함된다.
- 표 중심 문서가 많다.
- 한국어와 영어가 혼합될 수 있다.
- 단위 표기는 다양하다.
- 항목명 표현도 회사별로 다르다.

초기 MVP는 다음으로 제한한다.

- 텍스트 추출이 가능한 시험성적서
- 표 구조가 비교적 명확한 문서
- 10~20개 샘플 범위

스캔 품질이 너무 낮은 문서는 제외한다.

## 5. 구조화 파이프라인 설계

### 5.1 PDF 텍스트/표 추출

추천 라이브러리 후보:

- `pdfplumber`
- `PyMuPDF`
- `camelot`
- `tabula-py`
- `pandas`
- `re`

우선순위는 다음과 같다.

1. 텍스트 추출
2. 표 추출
3. OCR은 필요한 경우만 사용

페이지 단위로 처리한다.

- 페이지별 텍스트를 저장한다.
- 페이지별 표를 따로 저장한다.
- 원문 위치를 추적할 수 있게 한다.

OCR이 필요한 경우:

- 텍스트가 거의 없는 스캔본
- 표가 이미지로만 들어간 경우
- 글자 인식이 가능해야만 값이 보이는 경우

### 5.2 전처리

전처리는 단순하고 강하게 간다.

- 공백 정리
- 줄바꿈 정리
- 탭 정리
- 특수문자 정리
- 숫자와 단위 사이 공백 정리
- 소수점/쉼표 통일

예:

- `1,234` → `1234`
- `10 MPa` → `10 MPa`
- `10MPa` → `10 MPa`

### 5.3 필드 추출 규칙

추출은 규칙 기반 if/regex가 중심이다.

#### 날짜 패턴

- `YYYY-MM-DD`
- `YYYY.MM.DD`
- `YYYY/MM/DD`
- `YYYY년 MM월 DD일`

#### 로트번호

- `LOT`
- `Batch No.`
- `Lot No.`
- `로트번호`

#### 품목명

- 문서 상단 제목 우선
- `제품명`, `품명`, `시료명` 같은 라벨 우선
- 표 안에 반복되는 품목명은 보조 확인용

#### 표 추출

- 첫 열을 항목명 후보로 본다.
- 두 번째 열을 측정값 후보로 본다.
- 단위가 별도 열이면 단위 열을 우선 사용한다.
- `기준`, `Spec`, `LSL`, `USL` 같은 라벨을 같이 탐색한다.

### 5.4 필드명 정규화

표준화 규칙 예시는 다음과 같다.

- `시험일자`, `검사일`, `Date` → `issue_date`
- `제품명`, `품명`, `시료명` → `product_name`
- `로트번호`, `LOT`, `Batch No.` → `lot_no`
- `항목`, `시험항목`, `Item` → `item_name`
- `측정값`, `결과`, `Value` → `measured_value`
- `규격하한`, `하한`, `LSL` → `lower_spec`
- `규격상한`, `상한`, `USL` → `upper_spec`
- `판정`, `결과판정`, `Judgment` → `judgment`

### 5.5 단위 정규화

정규화 예시는 다음과 같다.

- `MPa`, `mpa`, `N/mm2` → `MPa`
- `wt%`, `%` → `%`
- `ppm`, `mg/L` → `ppm` 또는 `mg/L` 중 스키마 기준 하나로 통일

정규화 실패 시 처리:

- 원문 단위를 그대로 남긴다.
- `unit_normalized_status = FAILED` 같은 내부 플래그를 둔다.
- 실패 항목은 이상탐지에서 `NA`로 처리한다.

## 6. 이상탐지 규칙 설계

이상탐지는 규칙 기반 if문으로 처리한다.

### 6.1 기준 초과/미달

- 규칙 이름: `OUT_OF_RANGE_HIGH`
  - 조건: `measured_value > upper_spec`
  - 심각도: high
  - 메시지 예시: `측정값이 상한을 초과함`

- 규칙 이름: `OUT_OF_RANGE_LOW`
  - 조건: `measured_value < lower_spec`
  - 심각도: high
  - 메시지 예시: `측정값이 하한 미만임`

### 6.2 필수 항목 누락

- 규칙 이름: `REQUIRED_FIELD_MISSING`
  - 조건: 필수 필드가 비어 있음
  - 심각도: high
  - 메시지 예시: `필수 필드가 누락됨`

- 규칙 이름: `EMPTY_TABLE_VALUE`
  - 조건: 표는 있으나 값이 비어 있음
  - 심각도: medium
  - 메시지 예시: `표 행이 있으나 측정값이 비어 있음`

### 6.3 단위 불일치

- 규칙 이름: `UNIT_MISMATCH`
  - 조건: `measured_value` 단위와 `spec` 단위가 다름
  - 심각도: medium
  - 메시지 예시: `측정값 단위와 규격 단위가 다름`

- 규칙 이름: `UNIT_CONVERTIBLE`
  - 조건: 변환 가능한 단위 차이
  - 심각도: low
  - 메시지 예시: `단위 변환 후 비교 가능`

### 6.4 문서 내 충돌

- 규칙 이름: `DUPLICATE_ITEM_CONFLICT`
  - 조건: 동일 항목이 여러 번 나오는데 값이 다름
  - 심각도: high
  - 메시지 예시: `동일 항목의 값이 문서 내에서 상충함`

- 규칙 이름: `TABLE_TEXT_CONFLICT`
  - 조건: 표 값과 본문 값이 다름
  - 심각도: high
  - 메시지 예시: `표와 본문 값이 다름`

### 6.5 판정 불가

- 규칙 이름: `NO_SPEC_VALUE`
  - 조건: 규격값이 없음
  - 심각도: medium
  - 메시지 예시: `규격값이 없어 판정 불가`

- 규칙 이름: `NUMERIC_PARSE_FAILED`
  - 조건: 숫자 파싱 실패
  - 심각도: medium
  - 메시지 예시: `측정값 숫자 파싱 실패`

## 7. 출력 포맷 설계

### 7.1 JSON 구조

예시 스키마:

```json
{
  "document_name": "sample_test_report.pdf",
  "issue_date": "2026-03-27",
  "product_name": "Sample Product",
  "lot_no": "LOT-1234",
  "records": [
    {
      "item_name": "Tensile Strength",
      "measured_value": 12.3,
      "unit": "MPa",
      "lower_spec": 10.0,
      "upper_spec": 15.0,
      "judgment": "PASS",
      "source_page": 2,
      "raw_text": "..."
    }
  ],
  "anomalies": [
    {
      "rule": "OUT_OF_RANGE_HIGH",
      "severity": "high",
      "message": "측정값이 상한을 초과함"
    }
  ]
}
```

### 7.2 CSV 컬럼

엑셀에서 바로 열 수 있게 아래 컬럼을 쓴다.

- `document_name`
- `issue_date`
- `product_name`
- `lot_no`
- `item_name`
- `measured_value`
- `unit`
- `lower_spec`
- `upper_spec`
- `judgment`
- `source_page`
- `raw_text`

### 7.3 리포트

간단한 md 또는 txt 리포트 형식:

- 문서명
- 추출 성공률
- 이상 개수
- 누락 필드
- 재확인 필요 항목

예:

- `document_name: sample_test_report.pdf`
- `records: 12`
- `anomalies: 2`
- `missing_fields: lot_no, lower_spec`
- `review_required: 3`

## 8. 파일 구조 설계

예시 구조:

```text
project/
  data/
  samples/
  output/
  src/
    parser.py
    extractor.py
    normalizer.py
    validator.py
    reporter.py
    main.py
  tests/
```

각 파일 역할:

- `parser.py`
  - PDF/텍스트를 읽고 페이지별 텍스트/표를 꺼낸다.
- `extractor.py`
  - 라벨과 패턴으로 필드를 뽑는다.
- `normalizer.py`
  - 필드명과 단위를 표준화한다.
- `validator.py`
  - 이상탐지 규칙을 적용한다.
- `reporter.py`
  - JSON/CSV/MD 리포트를 만든다.
- `main.py`
  - 전체 파이프라인을 한 번에 실행한다.
- `tests/`
  - 샘플 문서 기준 회귀 테스트를 둔다.

## 9. 처리 흐름

```text
PDF 입력
→ 페이지 추출
→ 표/텍스트 파싱
→ 전처리
→ 필드 추출
→ 필드명 정규화
→ 단위 정규화
→ 이상탐지
→ JSON/CSV/리포트 출력
```

## 10. 검증 계획

검증은 10~20개 문서로 시작한다.

### 샘플 분류

- 단순 텍스트 기반 시험성적서
- 표 중심 시험성적서
- 표와 본문이 섞인 시험성적서

### 측정 방식

- 필드별 정확도
  - 정답과 추출값이 일치하는 비율
- 이상탐지 정확도
  - 초과/미달/누락을 제대로 잡는 비율
- 처리 시간
  - 문서 1건 처리 시간
- 재확인 항목 수
  - 사람이 다시 봐야 하는 항목 개수

### 간단한 지표

- precision/recall이 가능하면 사용한다.
- 초기에는 문서별 정확도와 필드별 정확도만으로도 충분하다.

### 시간 절감 측정

- 사람이 직접 정리한 시간과 비교한다.
- 문서 1건당 수작업 시간 vs 자동화 후 검수 시간으로 본다.

## 11. MVP 범위 / 제외 범위

| 구분 | 포함 |
|------|------|
| 포함 | 텍스트 기반 시험성적서 |
| 포함 | 기본 표 추출 |
| 포함 | 주요 필드 구조화 |
| 포함 | 규칙 기반 이상탐지 |
| 포함 | JSON/CSV/짧은 리포트 |
| 제외 | 자유서술 복잡 해석 |
| 제외 | 다양한 회사 포맷 완전 일반화 |
| 제외 | 로컬 LLM 자연어 설명 |
| 제외 | 클라우드 AI 연동 |
| 제외 | 대시보드/웹 UI |

## 12. 향후 확장

확장은 다음 순서로만 간다.

1. 규칙 확대
2. 문서군 확대
3. 로컬 모델을 설명/요약에만 제한적으로 추가
4. 온프레미스 에이전트화

이 섹션은 짧게 유지한다.

## 13. 최종 결론

규칙 기반부터 시작해야 하는 이유는 명확하다.

- 숫자와 단위가 핵심인 문서는 규칙이 더 안정적이다.
- 이상탐지는 판정 문제라 규칙이 더 잘 맞는다.
- 초기 제품 검증은 재현성과 신뢰성이 중요하다.
- 고객은 먼저 “정확히 추출되느냐”를 본다.

이 방식이 실제 제품 검증에 유리한 이유:

- 구현이 단순하다.
- 디버깅이 쉽다.
- 샘플 기준 검증이 가능하다.
- 회사별 config로 확장할 수 있다.

고객에게 보여줄 핵심 데모는 다음이다.

- 시험성적서 1건 업로드
- 핵심 필드 자동 추출
- 기준 초과/누락 자동 탐지
- JSON/CSV/리포트 자동 생성

## 부록 A. 초기 지원 라이브러리 후보

- `pdfplumber`
  - PDF 텍스트와 표를 추출한다.
- `PyMuPDF`
  - 페이지 렌더링과 텍스트 추출에 쓴다.
- `camelot`
  - 표 추출에 유용하다.
- `tabula-py`
  - 표 추출 보조 도구다.
- `pandas`
  - 표 데이터 정리와 CSV 저장에 쓴다.
- `re`
  - 정규식 기반 필드 추출에 쓴다.

## 부록 B. 필드 추출 규칙 예시 10개

1. `re.search(r'시험일자[:\s]*(\d{4}[./-]\d{2}[./-]\d{2})', text)`
2. `re.search(r'검사일[:\s]*(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)', text)`
3. `re.search(r'로트번호[:\s]*([A-Za-z0-9\-_/]+)', text)`
4. `re.search(r'LOT[:\s]*([A-Za-z0-9\-_/]+)', text, re.I)`
5. `re.search(r'제품명[:\s]*(.+)', text)`
6. `re.search(r'품명[:\s]*(.+)', text)`
7. `re.search(r'규격하한[:\s]*([0-9.,]+)', text)`
8. `re.search(r'하한[:\s]*([0-9.,]+)', text)`
9. `re.search(r'규격상한[:\s]*([0-9.,]+)', text)`
10. `re.search(r'상한[:\s]*([0-9.,]+)', text)`

## 부록 C. 이상탐지 규칙 예시 10개

1. `if measured_value > upper_spec: fail`
2. `if measured_value < lower_spec: fail`
3. `if lower_spec is None and upper_spec is None: judgment = "NA"`
4. `if product_name is empty: anomaly`
5. `if item_name is empty: anomaly`
6. `if unit is empty: anomaly`
7. `if measured_value cannot parse to number: anomaly`
8. `if table_value != body_value: anomaly`
9. `if duplicate item has conflicting values: anomaly`
10. `if unit conversion is impossible: review_required`

## 부록 D. 구현 우선순위

- 1순위: 텍스트 기반 PDF 파싱
- 2순위: 표 추출
- 3순위: 정규화 규칙
- 4순위: 이상탐지 규칙
- 5순위: 리포트 출력
- 6순위: 샘플 10~20개 검증
