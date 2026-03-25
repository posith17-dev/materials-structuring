# 특허 조성/물성 추출 프롬프트

```text
You are extracting structured material-composition and material-property records from a patent document.

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
1. Extract only records explicitly stated in the patent text, claims, examples, tables, or figure captions.
2. Prioritize alloy composition ranges, target process conditions, density/porosity, grain size, tensile properties, yield strength, elongation, hardness, and reduction in area.
3. Keep ranges exactly as written.
4. Keep units exactly as written.
5. If a claim states a minimum property requirement, preserve that wording in the value field.
6. If composition is given as a set of element percentages, keep it as a concise composition string.
7. If you are uncertain, omit the record rather than guessing.
8. source_excerpt must be a short supporting quote or precise paraphrase from the source chunk.
```
