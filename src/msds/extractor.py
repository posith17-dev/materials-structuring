from __future__ import annotations

import re


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _find_line_value(lines: list[str], label: str) -> str:
    def _is_direct_label(line: str) -> bool:
        stripped = line.strip()
        return (
            stripped == label
            or stripped.startswith(f"{label}:")
            or stripped.startswith(f"{label} ")
            or stripped.startswith(f"{label}\t")
        )

    for idx, line in enumerate(lines):
        if _is_direct_label(line):
            for nxt in lines[idx + 1 :]:
                nxt = nxt.strip()
                if nxt:
                    return nxt
    for idx, line in enumerate(lines):
        if label in line:
            for nxt in lines[idx + 1 :]:
                nxt = nxt.strip()
                if nxt:
                    return nxt
    return ""


def _line_or_next_value(line: str, lines: list[str], idx: int) -> str:
    if ":" in line:
        return _norm(line.split(":", 1)[-1])
    for nxt in lines[idx + 1 :]:
        nxt = nxt.strip()
        if nxt:
            return _norm(nxt)
    return ""


def _find_section(lines: list[str], start_label: str, end_label: str | None = None) -> list[str]:
    start = None
    end = len(lines)
    for idx, line in enumerate(lines):
        if start is None and start_label in line:
            start = idx + 1
            continue
        if start is not None and end_label and end_label in line:
            end = idx
            break
    if start is None:
        return []
    return [line.strip() for line in lines[start:end] if line.strip()]


def _record(
    material_name: str,
    composition: str,
    property_name: str,
    property_value: str,
    property_unit: str = "",
    test_condition: str = "",
    source_page: str = "본문",
    source_excerpt: str = "",
) -> dict[str, str]:
    return {
        "material_name": material_name,
        "composition": composition,
        "property_name": property_name,
        "property_value": property_value,
        "property_unit": property_unit,
        "test_condition": test_condition,
        "source_page": source_page,
        "source_excerpt": source_excerpt,
    }


def parse_msds_records(text: str) -> list[dict[str, str]]:
    lines = [line.rstrip() for line in text.splitlines()]
    material_name = ""
    for idx, line in enumerate(lines):
        if "제품명" in line:
            material_name = _norm(_find_line_value(lines[idx:], "제품명"))
            break
    if not material_name:
        material_name = _norm(_find_line_value(lines, "MSDS 상세정보"))

    cas_no = _norm(_find_line_value(lines, "CAS No"))
    composition_section = _find_section(lines, "구성성분", "노출기준")
    physical_section = _find_section(lines, "물리화학적 특성", "10.")
    exposure_section = _find_section(lines, "노출기준", "물리화학적 특성")

    records: list[dict[str, str]] = []
    if material_name:
        records.append(_record(material_name, "", "product_name", material_name, source_excerpt=material_name))
    if cas_no:
        records.append(_record(material_name, "", "CAS No", cas_no, source_excerpt=f"CAS No {cas_no}"))

    comp_material = ""
    comp_ratio = ""
    for idx, line in enumerate(composition_section):
        if line.startswith("물질명"):
            comp_material = _line_or_next_value(line, composition_section, idx)
        if line.startswith("함유량"):
            comp_ratio = _line_or_next_value(line, composition_section, idx)
    if comp_material:
        records.append(_record(material_name, comp_material, "composition", comp_material, source_excerpt=comp_material))
    if comp_ratio:
        records.append(_record(material_name, comp_material or material_name, "composition_ratio", comp_ratio, "%", source_excerpt=f"함유량 {comp_ratio}"))

    for idx, line in enumerate(exposure_section):
        if line.startswith("국내규정"):
            value = _line_or_next_value(line, exposure_section, idx)
            records.append(_record(material_name, "", "exposure_limit_domestic", value, source_excerpt=line))
        elif line.startswith("ACGIH 규정"):
            value = _line_or_next_value(line, exposure_section, idx)
            records.append(_record(material_name, "", "exposure_limit_acgih", value, source_excerpt=line))
        elif line.startswith("기타 노출기준"):
            value = _line_or_next_value(line, exposure_section, idx)
            records.append(_record(material_name, "", "exposure_limit_other", value, source_excerpt=line))

    physical_map = {
        "성상": ("physical_state", ""),
        "색상": ("color", ""),
        "녹는점/어는점": ("melting_point", "℃"),
        "초기 끓는점과 끓는점 범위": ("boiling_point_range", "℃"),
        "인화점": ("flash_point", "℃"),
        "증기압": ("vapor_pressure", "kPa"),
        "용해도": ("solubility", "g/100mL"),
        "비중": ("specific_gravity", ""),
    }
    for idx, line in enumerate(physical_section):
        for label, (prop_name, unit) in physical_map.items():
            if line.startswith(label):
                value = _line_or_next_value(line, physical_section, idx)
                records.append(
                    _record(
                        material_name,
                        "",
                        prop_name,
                        value,
                        unit,
                        test_condition="20℃" if "20℃" in value else "15℃" if "15℃" in value else "",
                        source_excerpt=line,
                    )
                )
                break

    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for rec in records:
        key = (rec["property_name"], rec["property_value"], rec["composition"])
        if not rec["property_value"]:
            continue
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rec)
    return deduped
