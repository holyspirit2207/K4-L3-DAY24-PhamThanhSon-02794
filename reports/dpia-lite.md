# DPIA-lite

Đây là bản mô tả cho bài lab, chạy bằng mock trên dữ liệu giả, không phải hồ sơ đánh giá tác động theo quy định pháp luật.

1. Loại dữ liệu và phân loại: ticket hỗ trợ trong `corpus/` được xếp `internal`, và có thể chứa chỉ thị do attacker cài vào. Hồ sơ khách trong `data/customers.json` gồm tên, CCCD, số điện thoại, số tài khoản và email, được xếp `restricted`. Toàn bộ là dữ liệu tổng hợp do repo tạo ra, không có người thật.

2. Mục đích xử lý và principal: người dùng muốn tóm tắt các ticket còn mở. `support_l1` chỉ được tìm ticket (`search_docs`). `dpo` được đọc hồ sơ khách cho mục đích `support-reply`. Principal được chọn bằng `--as` và tra trong `data/principals.json`; đây là mô phỏng, không có bước xác thực ai đang chạy lệnh.

3. Dữ liệu đi qua những run/tool nào, endpoint nào: Run A gọi `search_docs` đọc ticket, rồi chỉ lấy số ticket từ tên file. Run B nhận danh sách số đó, tra `related_tickets` để biết khách nào liên quan, và hỏi policy trước mỗi lần `read_customer`. Nếu nội dung ticket đòi gửi dữ liệu đi, runner hỏi policy cho `http_post` tới `http://127.0.0.1:10024/reconcile`. Đó là sink chạy localhost, endpoint duy nhất được phép. Mọi quyết định đều ghi vào `reports/ledger.jsonl`; ledger chỉ lưu hash của tham số, không lưu hồ sơ.

4. Bằng chứng deny/allow và giới hạn của mock: trước khi sửa, `reports/attack-before.log` có 4 POST chứa hồ sơ giả của `KH-000999`, mỗi biến thể lure một dòng. Sau khi sửa, chạy đúng câu hỏi đó với `--as dpo` thì `reports/attack-after.log` rỗng (0 byte). Ledger có 46 dòng, `verify()` trả True; dòng 23 và 46 là `http_post` bị deny với reason "restricted data cannot cross an egress-enabled boundary" và `on_behalf_of = dpo`. Với `support_l1`, mọi `read_customer` đều bị deny.

   Các giới hạn còn lại:
   - LLM là mock, nhận diện chỉ thị bằng danh sách marker; model thật có thể bị lừa theo cách khác.
   - Quyền principal là giả lập, không có đăng nhập hay token thật.
   - Regex PII đạt 100% trên bộ mẫu nhưng phụ thuộc nhãn như "CCCD", "STK"; số viết trần sẽ bị bỏ sót, và tên người không được che.
   - Hash chain chỉ phát hiện sửa dòng ở giữa file, không phát hiện xoá dòng cuối hay viết lại cả file.
   - Khi chạy cả corpus với `dpo`, Run B đọc 21 hồ sơ, tức mọi khách gắn với 45 ticket tìm được, dù bản tóm tắt không dùng tới. Cách làm này qua được test nhưng chưa tối thiểu hoá dữ liệu; hệ thống thật nên chỉ đọc hồ sơ khi câu trả lời thật sự cần.
