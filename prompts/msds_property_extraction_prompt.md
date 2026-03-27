# MSDS 물성/노출 정보 추출 프롬프트

```text
You are extracting structured material-property records from an MSDS document.

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
1. Extract only records explicitly stated in the MSDS text.
2. Prioritize product name, CAS number, composition, concentration, exposure limits, physical state, color, odor, boiling point, flash point, vapor pressure, solubility, and specific gravity/density when present.
3. Keep units exactly as written.
4. If composition values are listed per substance, keep each explicit value as a separate record.
5. If the condition or source basis is stated (for example ICSC, IUCLID, domestic regulation, 20℃), preserve it in test_condition.
6. If you are uncertain, omit the record rather than guessing.
7. source_excerpt must be a short supporting quote or precise paraphrase from the source chunk.
8. Prefer concise, database-friendly property names such as exposure_limit, physical_state, color, flash_point, boiling_point, vapor_pressure, solubility, specific_gravity.
```
