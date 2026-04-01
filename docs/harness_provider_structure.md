# 하네스 Provider 구조

이 문서는 하네스에 `OpenAI / Claude / Gemini`를 어떻게 붙일지 정리한다.

핵심 원칙은 다음과 같다.

- task type과 provider를 분리한다.
- task는 `classify`, `summarize`, `deep_review`처럼 정의한다.
- provider는 `openai`, `anthropic`, `gemini`처럼 정의한다.
- 기본 provider가 실패하면 로컬 fallback으로 내려간다.

## 1. 현재 권장 구조

```text
task
→ policy
→ executor
→ provider client
→ remote model
→ local fallback
```

즉, executor가 직접 OpenAI만 바라보지 않고, provider client를 통해 호출한다.

## 2. 역할 분리

### task layer

- 무엇을 할지 정의
- 예: `summarize`, `classify`, `deep_review`

### provider layer

- 어디에 요청할지 정의
- 예: `openai`, `anthropic`, `gemini`

### model layer

- provider 안에서 어떤 모델을 쓸지 정의
- 예:
  - OpenAI: `gpt-5.4-mini`, `gpt-5.4`
  - Anthropic: `claude-sonnet`, `claude-opus`
  - Gemini: `gemini-2.5-flash`, `gemini-2.5-pro`

## 3. 현재 코드 기준

현재는 아래 파일이 provider 레이어 역할을 한다.

- [model_client.py](/home/ubuntu/materials-structuring/src/common/harness/model_client.py)

지원 구조:

- `call_model(provider=..., model=..., prompt_text=...)`
- provider별 출력 텍스트 추출 함수 포함

현재 들어간 provider:

- `openai`
- `anthropic`
- `gemini`

## 4. 추천 매핑

| task_type | 기본 provider | 기본 모델 |
|---|---|---|
| `classify` | `openai` | `gpt-5.4-mini` |
| `summarize` | `openai` | `gpt-5.4-mini` |
| `draft` | `openai` | `gpt-5.4-mini` |
| `compare_multi_doc` | `openai` | `gpt-5.4` |
| `deep_review` | `openai` | `gpt-5.4` |

나중에는 회사 요구나 비용 정책에 따라 바꿀 수 있다.

예:

- `summarize` → `gemini`
- `deep_review` → `anthropic`

provider별 기본 모델은 내부적으로 다르게 둔다.

- OpenAI
  - `gpt-5.4-mini`, `gpt-5.4`
- Anthropic
  - `claude-3-5-sonnet-latest`
- Gemini
  - `gemini-2.5-pro`

## 5. fallback 순서 예시

### 소형 작업

`openai -> anthropic -> gemini -> local`

### 대형 작업

`openai -> anthropic -> local`

실제 운영에서는 모든 provider를 다 붙이기보다, 먼저 2개만 붙이는 편이 관리가 쉽다.

## 6. 환경변수 예시

- OpenAI
  - `OPENAI_API_KEY`
- Claude
  - `ANTHROPIC_API_KEY`
- Gemini
  - `GEMINI_API_KEY` 또는 `GOOGLE_API_KEY`

## 7. CLI 예시

직접 task를 실행할 때는 provider 하나 또는 provider 체인을 명시할 수 있다.

```bash
python3 /home/ubuntu/materials-structuring/scripts/run_harness_task.py \
  --task-type summarize \
  --document-type test_certificate \
  --providers openai,anthropic,gemini \
  --output-dir /home/ubuntu/materials-structuring/outputs/harness_summarize_smoke \
  --prompt "Return one short Korean sentence summarizing this COA sample."
```

`classify`는 labels를 같이 넘기는 편이 좋다.

```bash
python3 /home/ubuntu/materials-structuring/scripts/run_harness_task.py \
  --task-type classify \
  --document-type test_certificate \
  --providers openai,anthropic,gemini \
  --labels coa,msds \
  --output-dir /home/ubuntu/materials-structuring/outputs/harness_classify_smoke \
  --prompt "Classify this document as coa or msds. Certificate of Analysis / Mill Test Report."
```

## 8. 한 줄 결론

하네스는 task를 기준으로 움직이고, provider는 교체 가능한 하위 계층으로 두는 구조가 가장 안정적이다.
