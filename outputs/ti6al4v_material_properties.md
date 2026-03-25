# Ti-6Al-4V 물성 추출 실험

출처 논문:
- `/home/ubuntu/materials-structuring/samples/ti6al4v_superconducting_cavity.pdf`

## 추출 표

| 소재명/조성 | 물성 | 값 | 단위 | 실험조건 | 테이블/그림 출처 |
|---|---:|---:|---|---|---|
| Ti-6Al-4V | 조성(Ti) | 90 | wt% | EDS, acid polish 후 표면 조성 분석 | Fig. 1C |
| Ti-6Al-4V | 조성(Al) | 6 | wt% | EDS, acid polish 후 표면 조성 분석 | Fig. 1C |
| Ti-6Al-4V | 조성(V) | 4 | wt% | EDS, acid polish 후 표면 조성 분석 | Fig. 1C |
| Ti-6Al-4V | 조성(Fe 불순물) | <0.5 | wt% | EDS, acid polish 후 표면 조성 분석 | Fig. 1C |
| Ti-6Al-4V (90% Ti, 6% Al, 4% V by weight) | 초전도 전이온도 | 4.5 | K | 4-point DC resistance, 90% drop value, Quantum Design PPMS | Fig. 2, 본문 Page 2 |
| Ti-6Al-4V | 낮은 초전도 전이온도 | 0.95 | K | heat capacity 측정, equilibrium temperature 기준 | Fig. 2, 본문 Page 2 |
| AM Ti-6Al-4V conical resonator | 공진 주파수 | 7.50 | GHz | 20 mK에서 측정 | 본문 Page 3-4 |
| Ti-6Al-4V conical resonator | kinetic inductance fraction, αKI | 4×10^-3 ± 2×10^-3 |  | fractional frequency shift vs temperature를 two-fluid model로 fit | 본문 Page 4, Fig. 4 |
| Ti-6Al-4V conical resonator | 초전도 전이온도(Tc, fit) | 0.95 ± 0.1 | K | fractional frequency shift fit | 본문 Page 4, Fig. 4 |
| Ti-6Al-4V | London penetration depth, λ0 | 8 ± 3 | µm | magnetic participation ratio 528 m^-1 사용, microwave surface impedance 기반 추출 | 본문 Page 4, Fig. 4 |
| Ti-6Al-4V resonator | 내부 품질계수, Qi | ≈ 3×10^4 |  | quantum regime | 본문 Page 4 |
| Ti-6Al-4V conical geometry | magnetic participation ratio | 528 | m^-1 | ANSYS HFSS/COMSOL 계산 | 본문 Page 4 |

## 메모

- 이 논문은 기계적 물성보다 초전도/전자기 물성 중심이다.
- 인장강도, 항복강도, 연신율, 경도, 탄성계수 등은 직접 제시되지 않았다.
- 첫 실험으로는 "본문 + 그림 캡션에서 수치형 물성을 구조화할 수 있는가" 확인용으로 충분하다.
