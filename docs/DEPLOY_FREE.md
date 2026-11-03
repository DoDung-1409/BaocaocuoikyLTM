# Triển khai ConnectHub (ghi chú)

Ứng dụng có thể triển khai lên một nền tảng hosting Python và dùng PostgreSQL làm cơ sở dữ liệu.

Các bước tổng quát:
1. Đưa source code lên GitHub.
2. Tạo Web Service từ repository.
3. Cài dependencies bằng `pip install -r requirements.txt`.
4. Thiết lập `APP_ENV=production`, `SECRET_KEY` và `DATABASE_URL`.
5. Chạy migration bằng `flask db upgrade`.
6. Khởi chạy ứng dụng bằng Gunicorn với worker tương thích Socket.IO.
7. Truy cập website và kiểm tra đăng ký, tạo phòng, tham gia phòng và chat giữa hai tài khoản.

Ảnh đại diện được lưu trên local filesystem. Trên dịch vụ hosting có filesystem tạm thời, ảnh có thể mất sau khi restart/redeploy; tính năng này không ảnh hưởng tới tin nhắn văn bản lưu trong database.
