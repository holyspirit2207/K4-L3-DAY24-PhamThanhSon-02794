# Verification — điền trước khi nộp

- OS / Python / Gitleaks version:
- `python -m pytest tests/ -q`:
- `pre-commit run --all-files`:
- Ledger verify:
- Các lỗi còn lại:

## PII gate (CP3a)

Lệnh: `python -m pytest tests/test_pii.py -v -s --basetemp=.pytest_tmp`

Kết quả trên `tests/vn_pii_testset.jsonl`: gold=118, pred=118, tp=118, tức precision 1.000 và recall 1.000. Cả hai test đều pass.

Regex trong `agent/pii.py` dựa vào nhãn đứng trước giá trị. CCCD phải đi sau chữ "CCCD" hoặc "căn cước", số điện thoại phải đi sau "SĐT" hoặc "điện thoại", số tài khoản phải đi sau "STK" hoặc "tài khoản". Cách này tránh nhầm giữa CCCD 12 số và số tài khoản 8–16 số, nhưng nếu ai đó viết số trần không kèm nhãn, hoặc dùng nhãn khác như "ĐT" hay "acc", thì regex sẽ bỏ sót. Điểm 100% chỉ đúng với bộ mẫu synthetic của lab, chưa nói được gì về dữ liệu thật. Tên người không được che vì đề không yêu cầu loại PERSON.
