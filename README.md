# materials-structuring

소재/과학 문서에서 구조화 데이터를 추출하는 실험용 프로젝트입니다.

현재 목표는 "기초과학"이 아니라 **과학 데이터 구조화**입니다.

핵심 기술 축:
- PDF/HTML 파싱
- 표/문단 추출
- LLM 기반 정보 추출
- 정규화 스키마 적재
- 사람이 빠르게 검수 가능한 출력

## 현재 우선순위

1. 논문 PDF 1편에서 물성 추출 실험
2. 최소 스키마로 JSON/CSV 구조화
3. 사람이 5분 안에 검수 가능한지 확인

사업화/장기 확장은 나중 문제로 두고, 먼저 **"진짜로 뽑히는가"**를 확인합니다.

## 폴더 구조

```text
/home/ubuntu/materials-structuring/
├── README.md
├── .gitignore
├── docs/
├── prompts/
├── samples/
├── scripts/
└── outputs/
```

## 첫 실험 후보

- 논문 PDF 물성 추출
  - 소재명
  - 조성
  - 물성명
  - 값
  - 단위
  - 실험 조건

실험 스크립트:

```bash
python3 /home/ubuntu/materials-structuring/scripts/material_property_experiment.py \
  --input /home/ubuntu/materials-structuring/samples/paper.pdf \
  --output /home/ubuntu/materials-structuring/outputs/material_property_experiment.json
```

주의:
- PDF는 `pypdf`가 설치돼 있어야 텍스트 추출이 됩니다.
- PDF가 막히는 소스는 HTML 본문으로도 같은 스크립트를 돌릴 수 있습니다.
- 지금은 LLM 호출까지 자동화하지 않고, 추출용 JSON 스텁을 만드는 단계입니다.

## 이후 확장 후보

- 특허에서 조성 추출
- 시험성적서/COA/사양서 구조화
- 연구실 시뮬레이션 결과 정규화

## 운영 원칙

- 화려한 장기 계획보다 작은 추출 실험을 먼저 한다
- PDF 1개에서 10개 필드를 뽑는 것부터 시작한다
- 출력은 반드시 구조화 JSON/CSV로 남긴다
- 검수 가능한 수준인지 먼저 보고, 그다음 자동화를 늘린다
