# MSDS Validation Plan

이 문서는 RoboQC의 기존 `reader -> inspect -> report` 구조를 MSDS 공개 문서에 그대로 적용하는 검증 계획이다.

## 목표

- 공개 MSDS 문서 10건을 구조화한다.
- 같은 스키마로 JSON 레코드를 생성한다.
- 사람이 5분 안에 결과를 검수할 수 있는지 본다.

## 입력 문서

우선순위:

1. 안전보건공단 공개 MSDS 상세 페이지
2. 공개 MSDS HTML 샘플
3. 공개 PDF 또는 HTML로 변환한 MSDS 샘플

## 검증 항목

- 제품명
- CAS No
- 구성성분
- 함유량
- 노출기준
- 성상
- 색상
- 녹는점/어는점
- 끓는점 범위
- 인화점
- 증기압
- 용해도
- 비중

## 배치 실행

```bash
python3 /home/ubuntu/materials-structuring/scripts/msds_batch_validate.py \
  --input-dir /home/ubuntu/materials-structuring/samples/msds_batch \
  --output-dir /home/ubuntu/materials-structuring/outputs/msds_batch_validation \
  --limit 10
```

## 판정 기준

- `PASS`: 10건 중 핵심 필드가 안정적으로 추출됨
- `PARTIAL`: 일부 필드는 잘 나오지만 구조화가 불안정함
- `FAIL`: JSON 구조화가 불안정하거나 핵심 필드가 거의 안 잡힘

## 다음 단계

- 공개 문서 10건으로 안정성 확인
- 시험성적서/COA로 동일 파이프라인 확장
- 도메인 어댑터만 바꿔서 다른 문서군에 재사용
