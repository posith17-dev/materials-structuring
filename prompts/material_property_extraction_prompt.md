# 물성 추출 프롬프트 초안

아래는 논문/기술문서 텍스트에서 물성 정보를 구조화하기 위한 최소 프롬프트 초안입니다.

```text
You are extracting structured material-property records from a scientific paper.

Return only valid JSON.

Schema:
{
  "records": [
    {
      "material_name": "",
      "composition": "",
      "property_name": "",
      "property_value": "",
      "property_unit": "",
      "test_condition": "",
      "source_page": "",
      "source_excerpt": ""
    }
  ]
}

Rules:
1. Extract only records explicitly stated in the text.
2. Keep units exactly as written.
3. If composition is not explicit, leave it empty.
4. If the property value is given as a range, keep the original range string.
5. If you are uncertain, omit the record rather than guessing.
6. `source_excerpt` must be a short supporting quote or paraphrase from the text chunk.
```
