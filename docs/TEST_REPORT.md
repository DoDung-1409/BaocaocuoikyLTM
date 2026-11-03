# Báo cáo kiểm thử ConnectHub (phiên bản rút gọn)

Sau khi loại bỏ các chức năng chia sẻ file trong phòng chat và Online/Offline, bộ kiểm thử tập trung vào:
- Đăng ký, đăng nhập và bảo vệ phiên.
- Tạo phòng, tham gia phòng, rời phòng và quyền chủ phòng.
- Gửi tin nhắn văn bản qua Socket.IO.
- Lưu và truy vấn lịch sử tin nhắn.
- Kiểm tra dữ liệu đầu vào và phân quyền.
- Cập nhật và tải ảnh đại diện.

Chạy kiểm thử bằng `pytest`. Kết quả cần được ghi nhận trực tiếp từ lần chạy trên môi trường hiện tại trước khi sử dụng con số trong báo cáo học phần.
