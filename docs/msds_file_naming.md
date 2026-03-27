# MSDS File Naming Rule

이 문서는 MSDS 배치 입력 파일의 파일명 규칙을 정한다.

## 목표

- 파일만 봐도 물질을 알아볼 수 있게 한다.
- 검색 키를 제품명과 CAS No.로 통일한다.
- HTML, TXT, PDF가 섞여도 같은 규칙으로 찾을 수 있게 한다.

## 권장 형식

```text
msds_{product_slug}_{cas_no}.{ext}
```

예시:

- `msds_dodecanenitrile_2437-25-4.txt`
- `msds_dodecanenitrile_2437-25-4.html`
- `msds_dodecanenitrile_2437-25-4.pdf`

## slug 규칙

- 한글 제품명은 가능하면 영문/숫자 slug로 변환한다.
- 공백은 `_`로 바꾼다.
- 특수문자는 제거하거나 `-`로 단순화한다.
- CAS No.는 그대로 넣되, 파일명에서는 `.` 대신 `-` 또는 `_`를 쓴다.

예:

- `도데칸니트릴 (CAS No. 2437-25-4)` -> `msds_dodecanenitrile_2437-25-4.txt`

## 예외

- 확인용 baseline 파일은 소스 식별자 이름을 유지할 수 있다.
- 단, 배치에 넣을 때는 가능하면 제품명/CAS 기준으로 맞춘다.

## 검색 기준

1. CAS No.
2. 제품명
3. 이명 / 동의어

예:

```bash
rg -n "2437-25-4|도데칸니트릴" /home/ubuntu/materials-structuring
```

## 운영 원칙

- 새 샘플은 이 규칙으로 저장한다.
- 원본 제목은 파일명보다 manifest / report에 남긴다.
- 같은 물질의 HTML/TXT/PDF는 같은 stem을 공유하되 확장자로 구분한다.
