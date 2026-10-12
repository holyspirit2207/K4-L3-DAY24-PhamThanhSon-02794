# Baseline

1. Baseline chưa tạo `agent_id`, `run_id` hay nhận danh tính người dùng để kiểm quyền. `_naive_loop()` đi thẳng từ `search_docs()` sang xử lý nội dung trả về tại `agent/loop.py:27-34`, nên mọi lần chạy đều thiếu ngữ cảnh OBO.

2. Không có policy nào kiểm tra mục đích, quyền hoặc phân loại dữ liệu trước khi gửi. Nội dung ticket vốn là dữ liệu không tin cậy nhưng `find_injection()` lại diễn giải chỉ thị bên trong như lệnh; sau đó chính luồng baseline quyết định gọi `read_customer()` tại `agent/loop.py:39` và `http_post()` tại `agent/loop.py:44`. Allowlist trong `agent/tools.py:68-83` chỉ giữ URL ở localhost, không quyết định record nào được phép gửi.

3. Body được tạo ngay tại `agent/loop.py:44` dưới dạng `{"records": collected}`. Sink nhận body rồi ghi trường `path` và `body` vào `reports/sink.log` tại `sink/sink.py:44-47`; đây là nơi đối chiếu để chứng minh hồ sơ synthetic đã tới đích thử nghiệm.
