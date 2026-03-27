# MSDS Batch Inputs

이 폴더는 공개 MSDS 검증용 입력 샘플을 모아두는 곳입니다.

## 권장 파일명

- `msds_01_baseline.html`
- `msds_02_methacrylic_acid.html`
- `msds_03_dimethyl_carbamoyl_chloride.html`
- `msds_04_2_nitropropane.html`
- `msds_05_mancozeb.html`
- `msds_06_isobutyric_acid.html`
- `msds_07_tetrachloroethane_1122.html`
- `msds_08_chlorosulfonic_acid.html`
- `msds_09_thallium_chloride.html`
- `msds_10_cobalt_chloride_hexahydrate.html`

## 사용 방법

1. 공개 MSDS HTML 또는 PDF를 이 폴더에 넣는다.
2. 파일명을 위 권장 형식으로 바꾼다.
3. 다음 명령으로 배치 검증을 실행한다.

```bash
python3 /home/ubuntu/materials-structuring/scripts/msds_batch_validate.py \
  --input-dir /home/ubuntu/materials-structuring/samples/msds_batch \
  --output-dir /home/ubuntu/materials-structuring/outputs/msds_batch_validation \
  --limit 10
```

## 메모

- 이미 확인된 baseline 샘플은 `msds_kosha_000939_sample.html`이다.
- 이 폴더는 공개 문서를 넣어 두고 재현 가능한 배치 검증을 하는 용도다.
