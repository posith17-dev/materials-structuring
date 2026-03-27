# MSDS Public Candidate Checklist

이 문서는 RoboQC의 MSDS 구조화 검증용 공개 입력 10건을 모아둔 체크리스트다.
기준은 `reader -> inspect -> report` 파이프라인을 그대로 재사용하는 것이다.
파일명 규칙은 [MSDS File Naming Rule](/home/ubuntu/materials-structuring/docs/msds_file_naming.md) 을 따른다.

## Confirmed baseline

1. [도데칸니트릴 (CAS No. 2437-25-4)](/home/ubuntu/materials-structuring/samples/msds_batch/msds_dodecanenitrile_2437-25-4.html)
   - source: 안전보건공단 MSDS 상세 페이지
   - status: rule validation completed

## Next public MSDS candidates

2. [메타크릴 산](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
   - page: 유해/위험성정보 37/300
   - target: row 361

3. [디메틸 카르바모일클로라이드](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
   - page: 유해/위험성정보 37/300
   - target: row 362

4. [2-니트로프로판](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
   - page: 유해/위험성정보 37/300
   - target: row 363

5. [만코제브](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
   - page: 유해/위험성정보 37/300
   - target: row 364

6. [아이소뷰틸 산](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
   - page: 유해/위험성정보 37/300
   - target: row 365

7. [1,1,2,2-테트라클로로에탄](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
   - page: 유해/위험성정보 37/300
   - target: row 366

8. [클로로술폰산](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
   - page: 유해/위험성정보 37/300
   - target: row 367

9. [탈륨 염화물](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
   - page: 유해/위험성정보 37/300
   - target: row 368

10. [코발트 염화물, 헥사수화물](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
    - page: 유해/위험성정보 37/300
    - target: row 369

11. [염화니켈 헥사하이드레이트](https://msds.kosha.or.kr/MSDSInfo/kcic/chemIList.do?pageIndex=37)
    - page: 유해/위험성정보 37/300
    - target: row 370

## Batch order

추천 순서:

1. Confirmed baseline 1건으로 파이프라인 고정
2. row 361~370 순서대로 10건 수집
3. 각 문서를 `samples/msds_batch/`에 넣고 `msds_batch_validate.py`로 실행
   - HTML / PDF / TXT 모두 가능
4. `records` 수와 핵심 필드 추출 여부를 비교

## 검증 포인트

- product name
- CAS No
- composition
- exposure limits
- physical state
- color
- melting point
- boiling point range
- flash point
- vapor pressure
- solubility
- specific gravity

## 결과 판정

- `PASS`: 공개 MSDS 10건 중 핵심 필드가 안정적으로 구조화됨
- `PARTIAL`: 일부 필드는 잘 나오지만 문서군별 편차가 큼
- `FAIL`: 문서에서 구조화 가능한 필드가 거의 없음
