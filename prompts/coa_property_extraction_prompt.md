# COA/시험성적서 물성 추출 프롬프트

```text
You are extracting structured material-property records from a certificate of analysis (COA), mill test report, or material test certificate.

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
1. Extract only records explicitly stated in the report text.
2. Prioritize chemistry, tensile strength, yield strength, elongation, reduction in area, hardness, modulus, density, dimensions, and heat/lot identifiers when they are material-relevant.
3. Keep units exactly as written.
4. If composition values are listed element-by-element, keep each explicit value as a separate record.
5. If the condition is stated (for example solution treated, aged, annealed, room temperature), preserve it in test_condition.
6. If you are uncertain, omit the record rather than guessing.
7. source_excerpt must be a short supporting quote or precise paraphrase from the source chunk.
```
