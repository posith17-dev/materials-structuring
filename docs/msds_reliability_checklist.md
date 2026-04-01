# MSDS Reliability Checklist

이 문서는 MSDS 구조화 검증 결과를 믿을 수 있는지 확인하기 위한 체크리스트다.
목표는 "파이프라인이 돌아간다" 수준을 넘어서, **입력-출력-메타데이터가 서로 일치하는지** 확인하는 것이다.

## 1. 원본 출처 확인

- 문서의 원본 URL 또는 파일 출처가 남아 있는가
- 같은 물질의 HTML, TXT, PDF가 같은 출처에서 왔는가
- 수동 복사본인지, 자동 추출본인지 구분되는가

## 2. 파일명과 내용 일치

- 파일명이 `msds_{product_slug}_{cas_no}.{ext}` 형식인가
- 파일명에 적힌 제품명과 문서 본문 제품명이 일치하는가
- 파일명에 적힌 CAS No.와 본문 CAS No.가 일치하는가
- 다른 물질의 문서가 섞여 있지 않은가

## 3. 포맷별 교차 검증

- HTML, TXT, PDF가 같은 물질을 가리키는가
- 포맷이 달라도 핵심 필드가 유사하게 추출되는가
- 특정 포맷에서만 이상한 값이 나오지 않는가

## 4. 핵심 필드 검증

- product_name
- CAS No
- composition
- composition_ratio
- exposure_limit_domestic
- physical_state
- color
- melting_point
- boiling_point_range
- flash_point
- vapor_pressure
- solubility
- specific_gravity

## 5. 결과 일관성

- 같은 문서에 대해 반복 실행했을 때 결과가 크게 흔들리지 않는가
- record_count가 예상 범위 안에 있는가
- `자료없음`, `NULL`, 빈 문자열이 과도하게 많지 않은가

## 6. 이상 징후

- 파일명은 맞는데 본문 제품명이 다르다
- HTML과 TXT가 다른 물질로 나온다
- record_count가 비정상적으로 낮다
- 섹션 파싱이 끊겨서 필드가 대부분 빠진다

## 판정

- `PASS`: 파일명/내용 일치, 포맷별 교차 검증 통과, 핵심 필드가 안정적
- `REVIEW`: 일부 필드가 흔들리거나 포맷 간 차이가 큼
- `FAIL`: 다른 물질 혼입, 핵심 필드 대량 누락, 반복 실행 불안정

## 권장 운영

1. 새 샘플을 받으면 파일명부터 맞춘다.
2. HTML/TXT/PDF를 같은 물질 기준으로 묶는다.
3. 배치 리포트보다 먼저 이 체크리스트를 본다.
4. 이상 징후가 있으면 결과를 신뢰하지 말고 원본을 다시 확인한다.

