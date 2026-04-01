# Harness Status 2026-04-01

## 현재 상태

- 하네스 공통 계층이 추가되었다.
- `test_certificate`와 `msds`는 하네스 경유 실행이 가능하다.
- `small_model_executor`, `large_model_executor`는 provider 체인을 지원한다.
- 원격 모델 호출 실패 시 로컬 fallback으로 결과를 남긴다.

## 확인된 동작

### 규칙 기반

- MSDS 하네스 실행 성공
- 시험성적서/COA 하네스 실행 성공

### 모델 기반

- `classify`
- `summarize`
- `deep_review`

위 task들은 모두 하네스 경유로 실행되며, 원격 모델 호출 실패 시 fallback 결과와 메타데이터를 저장한다.

## provider 체인

현재 지원 provider:

- `openai`
- `anthropic`
- `gemini`
- `local fallback`

기본 흐름:

- 소형 작업: `openai -> anthropic -> gemini -> local`
- 대형 작업: `openai -> anthropic -> gemini -> local`

## 현재 제약

- OpenAI: quota 부족 상태
- Anthropic: API credit 부족 상태
- Gemini: 현재 계정/쿼터 상황에 따라 성공 또는 quota 제한 발생

즉, 구조 검증은 완료되었고, 원격 provider 품질/가용성은 별도로 관리해야 한다.

## 한 줄 결론

하네스 시스템은 초기 구현과 검증이 끝났고, 현재는 규칙 기반 코어 + provider 체인 + local fallback까지 동작하는 상태다.
