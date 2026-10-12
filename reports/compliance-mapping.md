# Compliance mapping

Bảng này nối các yêu cầu đề bài nêu với control đã làm trong lab. Tôi chưa đọc đối chiếu từng điều khoản trong văn bản gốc, nên cột điều khoản ghi "chưa xác minh". Đây là bài mô phỏng trên dữ liệu giả, không phải chứng nhận tuân thủ.

| Nguồn / chủ đề | Control đã làm | Evidence file:dòng | Giới hạn |
|---|---|---|---|
| Luật 91/2025/QH15 (Bảo vệ dữ liệu cá nhân) — xử lý đúng mục đích, giới hạn người được truy cập. Điều khoản: chưa xác minh | Policy chỉ cho đọc hồ sơ khi principal có tool và purpose phù hợp; `support_l1` bị chặn trước khi mở hồ sơ | `agent/policy.py:88`, `agent/policy.py:94`, `agent/runner.py:182-185` | Principal lấy từ `data/principals.json`, không có xác thực thật |
| Luật 91/2025/QH15 — không để dữ liệu cá nhân đi ra ngoài trái phép. Điều khoản: chưa xác minh | Rule restricted + egress luôn deny, kể cả với `dpo`; `http_post` chỉ chạy khi policy allow | `agent/policy.py:64`, `agent/runner.py:201-202`, `reports/ledger.jsonl` dòng 23 và 46, `reports/attack-after.log` (0 byte) | Sink chỉ là localhost; không kiểm các kênh rò rỉ khác |
| NĐ 356/2025/NĐ-CP — biện pháp kỹ thuật và ghi nhận hoạt động xử lý dữ liệu. Điều khoản: chưa xác minh | Che CCCD/SĐT/STK/email trước khi tóm tắt; ledger ghi mọi quyết định allow/deny kèm reason, chỉ lưu `args_hash` | `agent/pii.py:60-80`, `agent/runner.py:204`, `agent/runner.py:96-100`, `agent/ledger.py:53-91` | Regex dựa vào nhãn; hash chain không phát hiện việc xoá dòng cuối |
| Luật AI 134/2025/QH15 — hệ thống AI phải có kiểm soát và truy vết. Điều khoản: chưa xác minh | Mỗi tool call có `agent_id`, `run_id`, `on_behalf_of`, `expires_at`; quyền hết hạn thì deny | `agent/runner.py:100`, `agent/policy.py:83`, `reports/ledger.jsonl` | Dùng mock LLM, chưa thử với model thật |
| OWASP ASI01 — Agent Goal Hijack | Tách Run A/Run B; Run B chỉ nhận số ticket từ tên file và tra `related_tickets`, không lấy customer ID trong text | `agent/runner.py:124-140`, `tests/test_split.py`, `injection-corpus.md` | Chỉ thử 4 kiểu lure trong `corpus/` |
| OWASP ASI03 — Identity & Privilege Abuse | Quyền hiệu lực = giao của `allowed_tools`, `agent_scopes`, `parent_scopes`; unknown principal hoặc hết hạn thì deny | `agent/policy.py:74-98`, `tests/test_obo.py` | `--as` chỉ là mô phỏng chọn principal |
| OWASP ASI04 — Agentic Supply Chain | Lock dependency có hash; hook Gitleaks pin `v8.30.1`; quét lịch sử ra token giả | `requirements.lock`, `.pre-commit-config.yaml:3-6`, `reports/secrets-incident.md` | Không kiểm tool/plugin bên thứ ba ngoài pip |

Nguồn đã tra:
- Luật 91/2025/QH15: https://thuvienphapluat.vn/van-ban/Bo-may-hanh-chinh/Law-91-2025-QH15-Personal-Data-Protection-665440.aspx (trang tra cứu, chưa phải Công báo)
- NĐ 356/2025/NĐ-CP: https://vbpl.moj.gov.vn/TW/Lists/vbpq/Attachments/187276/ND.356.2025.doc (CSDL văn bản pháp luật của Bộ Tư pháp)
- Luật 134/2025/QH15: https://thuvienphapluat.vn/van-ban/Cong-nghe-thong-tin/Luat-Tri-tue-nhan-tao-2025-so-134-2025-QH15-679013.aspx (trang tra cứu, chưa phải Công báo)
- OWASP Top 10 for Agentic Applications 2026: https://genai.owasp.org/risk-maps-supported/top-10-for-agentic-apps-2026/
