# MSDS Batch Inputs

이 폴더는 공개 MSDS 검증용 입력 샘플을 모아두는 곳입니다.

권장 규칙은 [MSDS File Naming Rule](/home/ubuntu/materials-structuring/docs/msds_file_naming.md) 을 따른다.

## 권장 파일명

- `msds_dodecanenitrile_2437-25-4.html`
- `msds_dodecanenitrile_2437-25-4.txt`

HTML, PDF, TXT 모두 가능합니다.

## 사용 방법

1. 공개 MSDS HTML, PDF 또는 TXT를 이 폴더에 넣는다.
2. 파일명을 `msds_{product_slug}_{cas_no}.{ext}` 형식으로 바꾼다.
3. 다음 명령으로 배치 검증을 실행한다.

```bash
python3 /home/ubuntu/materials-structuring/scripts/msds_batch_validate.py \
  --input-dir /home/ubuntu/materials-structuring/samples/msds_batch \
  --output-dir /home/ubuntu/materials-structuring/outputs/msds_batch_validation \
  --limit 10
```

## 메모

- 이미 확인된 baseline 샘플은 `msds_dodecanenitrile_2437-25-4.html` / `msds_dodecanenitrile_2437-25-4.txt`다.
- 이 폴더는 공개 문서를 넣어 두고 재현 가능한 배치 검증을 하는 용도다.
