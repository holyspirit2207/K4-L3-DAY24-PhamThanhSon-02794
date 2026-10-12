"""BƯỚC 3a — PII gate TRƯỚC KHI vào context/store (12').

Đọc CHECKPOINTS.md (§3a) trước khi bắt đầu: Presidio không có tiếng Việt
sẵn (AnalyzerEngine() mặc định chỉ hỗ trợ "en"). Đường an toàn cho 2h là
regex recognizer + deny-list cho PERSON — coi spaCy/transformers NER là
stretch goal, KHÔNG bắt buộc.

Interface bắt buộc (tests/test_pii.py gọi trực tiếp 2 hàm này):

    detect(text: str) -> list[dict]
        Mỗi entity: {"type": str, "start": int, "end": int}
        `type` là một trong: "VN_CCCD", "VN_PHONE", "VN_BANK_ACCOUNT", "EMAIL"
        `start`/`end` là offset ký tự trong `text` (offset đầu bao gồm,
        offset cuối KHÔNG bao gồm — giống slice Python text[start:end]).
        Format này khớp với tests/vn_pii_testset.jsonl.

    redact(text: str) -> str
        Trả về `text` sau khi mọi entity từ detect() bị thay bằng
        "[REDACTED_<TYPE>]". Phải xử lý overlap/thứ tự đúng khi có nhiều
        entity (gợi ý: thay từ cuối văn bản về đầu để offset không bị lệch).

Gợi ý định dạng (không bắt buộc đúng regex này, miễn đạt ngưỡng trên test
set ở tests/vn_pii_testset.jsonl):
    VN_CCCD          12 chữ số liên tiếp
    VN_PHONE         0 + 9-10 chữ số, có thể có dấu cách/gạch ngang
    VN_BANK_ACCOUNT  8-16 chữ số liên tiếp, thường đi kèm "STK"/"số tài khoản"
    EMAIL            dạng chuẩn local@domain.tld

Đo bằng: pytest tests/test_pii.py -v -s   (in ra precision/recall)
"""
from __future__ import annotations

import re


_PATTERNS = (
    (
        "EMAIL",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        0,
    ),
    (
        "VN_CCCD",
        re.compile(r"\b(?:CCCD|căn\s*cước(?:\s*công\s*dân)?)\s*(?:của\s+[^:,.]{1,40}\s*)?(?::|là)?\s*(\d{12})\b", re.IGNORECASE),
        1,
    ),
    (
        "VN_PHONE",
        re.compile(r"\b(?:SĐT|số\s*điện\s*thoại|điện\s*thoại)\b[^\d]{0,50}(0(?:[ .-]?\d){9,10})\b", re.IGNORECASE),
        1,
    ),
    (
        "VN_BANK_ACCOUNT",
        re.compile(r"\b(?:STK|số\s*tài\s*khoản|tài\s*khoản)\b[^\d]{0,30}(\d{8,16})\b", re.IGNORECASE),
        1,
    ),
)


def detect(text: str) -> list[dict]:
    entities = []
    occupied: list[tuple[int, int]] = []

    for entity_type, pattern, group in _PATTERNS:
        for match in pattern.finditer(text):
            start, end = match.span(group)
            if any(start < used_end and used_start < end for used_start, used_end in occupied):
                continue
            entities.append({"type": entity_type, "start": start, "end": end})
            occupied.append((start, end))

    return sorted(entities, key=lambda entity: (entity["start"], entity["end"]))


def redact(text: str) -> str:
    redacted = text
    for entity in reversed(detect(text)):
        marker = f"[REDACTED_{entity['type']}]"
        redacted = redacted[:entity["start"]] + marker + redacted[entity["end"]:]
    return redacted
