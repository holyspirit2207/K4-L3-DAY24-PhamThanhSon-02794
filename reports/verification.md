# Verification — điền trước khi nộp

- OS / Python / Gitleaks version: Windows 11 (10.0.26300), Python 3.11.9, Gitleaks 8.30.1, pre-commit 4.6.2
- `python -m pytest tests/ -q`: 33 passed, 0 failed, 0 skipped (chạy với `--basetemp=.pytest_tmp`)
- `pre-commit run --all-files`: Passed
- Ledger verify: True, `reports/ledger.jsonl` có 46 dòng từ 2 lượt chạy `--as dpo`; dòng 23 và 46 là `http_post` deny
- Các lỗi còn lại: không còn test fail. Các lỗi môi trường đã gặp và cách xử lý nằm ở mục bên dưới.

## PII gate (CP3a)

Lệnh: `python -m pytest tests/test_pii.py -v -s --basetemp=.pytest_tmp`

Kết quả trên `tests/vn_pii_testset.jsonl`: gold=118, pred=118, tp=118, tức precision 1.000 và recall 1.000. Cả hai test đều pass.

Regex trong `agent/pii.py` dựa vào nhãn đứng trước giá trị. CCCD phải đi sau chữ "CCCD" hoặc "căn cước", số điện thoại phải đi sau "SĐT" hoặc "điện thoại", số tài khoản phải đi sau "STK" hoặc "tài khoản". Cách này tránh nhầm giữa CCCD 12 số và số tài khoản 8–16 số, nhưng nếu ai đó viết số trần không kèm nhãn, hoặc dùng nhãn khác như "ĐT" hay "acc", thì regex sẽ bỏ sót. Điểm 100% chỉ đúng với bộ mẫu synthetic của lab, chưa nói được gì về dữ liệu thật. Tên người không được che vì đề không yêu cầu loại PERSON.

## Kết quả theo checkpoint

| CP | Lệnh | Kết quả |
|---|---|---|
| 2 | `python -m agent.check_lure corpus/ticket-90*.md` | 4/4 lure sẵn sàng |
| 2 | chạy `_naive_loop` cho từng lure với sink đang nghe | `attack-before.log` 4 dòng, cả 4 có `KH-000999` |
| 3a | `pytest tests/test_pii.py -v -s` | 2 passed, gold=118 pred=118 tp=118 |
| 3b | `pytest tests/test_policy.py -v` | 4 passed |
| 3c | `pytest tests/test_obo.py -v` | 5 passed |
| 3d | `pytest tests/test_split.py tests/test_injection.py -v` | 1 + 8 passed, không SKIP |
| 3e | `pytest tests/test_ledger.py -v` | 3 passed |
| 4 | `gitleaks git --config .gitleaks.toml --redact .` | 1 finding ở `1bdd849`, exit 1 (dự kiến) |
| 4 | `gitleaks dir --config .gitleaks.toml --redact .` | lần đầu 1 false positive trong `.venv`, sau allowlist: sạch, exit 0 |
| 4 | `pip install --require-hashes -r requirements.lock` | exit 0 |
| 5 | `python -m agent.loop --mock --as dpo "Tổng hợp các ticket còn mở tuần này"` | `attack-after.log` 0 byte |

## Lỗi đã gặp và cách xử lý

- Pytest báo `PermissionError: [WinError 5]` ở `%TEMP%\pytest-of-Lenovo`, nên tôi chạy với `--basetemp=.pytest_tmp`.
- `sink.py` và `check_lure` lỗi `UnicodeEncodeError` trên console cp1252, nên tôi đặt `PYTHONIOENCODING=utf-8`.
- Hook pre-commit ban đầu truyền thêm `git ... .` vào `args`, trùng với entry gốc `gitleaks git --pre-commit --staged`; tôi sửa thành `args: [--config, .gitleaks.toml]`.
- Lần quét file đầu tiên ra false positive trong `.venv` (xem `secrets-incident.md`).
