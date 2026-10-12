# Secret giả trong lịch sử Git

- Scanner và phiên bản: Gitleaks 8.30.1, tải bản windows_x64 từ trang release chính thức trên GitHub và đã so sha256 với file checksums đi kèm.

- Commit chứa token giả: `1bdd849` (chore: seed student lab with synthetic secret exercise). File chứa token đã bị xoá ở commit sau, nhưng nội dung cũ vẫn còn trong lịch sử.

- File, rule và kết quả quét lịch sử: chạy `gitleaks git --config .gitleaks.toml --redact .` thì Gitleaks báo đúng 1 finding, rule `lab24-synthetic-token`, file `lab-fake-secret.txt` dòng 1, lệnh trả mã 1. Đây là token giả đề bài cố ý để lại, không phải sự cố thật. Vì có `--redact` nên giá trị token không bị in ra, và tôi cũng không chép nó vào báo cáo này.

- Kết quả quét file hiện tại: lần đầu chạy `gitleaks dir --config .gitleaks.toml --redact .` vẫn ra 1 finding, rule `generic-api-key`, nằm trong `.venv/Lib/site-packages/setuptools/_distutils/msvccompiler.py`. File này là thư viện cài vào virtualenv, không phải code của bài, và `.venv/` đã nằm trong `.gitignore`, nên tôi coi đây là false positive. Tôi thêm vào `.gitleaks.toml` một allowlist chỉ cho đường dẫn `^\.venv[\\/]`, không đụng tới rule bắt token giả. Chạy lại thì quét file hiện tại sạch (mã 0), còn quét lịch sử vẫn bắt được token ở `1bdd849`. Hook `gitleaks-system` pin `v8.30.1` chạy `pre-commit run --all-files` cũng Passed.

- Nếu đây là credential thật, cần xử lý thế nào: phải coi như token đã lộ từ lúc commit được push. Việc đầu tiên là vào dịch vụ cấp token để thu hồi rồi rotate sang token mới. Sau đó xem log sử dụng từ thời điểm commit tới nay để tìm truy cập bất thường. Token mới để trong secret manager hoặc biến môi trường, không để trong repo. Cuối cùng mới xử lý các bản sao: viết lại lịch sử bằng git filter-repo và báo những người đã fork hoặc clone. Bước này chỉ giảm khả năng token cũ bị đọc tiếp, chứ không làm nó hết hiệu lực.

- Vì sao xoá file khỏi HEAD hoặc pin dependency vẫn chưa đủ: xoá file ở commit mới không xoá được nội dung trong commit cũ, ai có bản clone vẫn đọc lại được, và lần quét lịch sử ở trên cho thấy đúng điều đó. Hash lock giúp chặn package bị tráo, hook giúp chặn secret mới lọt vào các commit sau, nhưng không cái nào làm token đã lộ hết hiệu lực. Chỉ bên phát hành token mới thu hồi được nó.
