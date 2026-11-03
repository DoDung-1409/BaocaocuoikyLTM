# Kiến trúc ConnectHub

Ứng dụng sử dụng mô hình Client–Server:

1. Trình duyệt hiển thị giao diện HTML/CSS/JavaScript.
2. Flask xử lý đăng nhập, phòng chat và API lịch sử tin nhắn.
3. Flask-SocketIO gửi/nhận sự kiện `message:send` và `message:new`.
4. SQLAlchemy lưu Users, Rooms, RoomMembers và Messages trong cơ sở dữ liệu.

Tin nhắn văn bản được lưu vào database trước khi phát tới các thành viên thuộc phòng. Server kiểm tra phiên đăng nhập và membership trước khi cho phép gửi.

Ảnh đại diện được lưu local. Bản chat nhóm này không triển khai gửi file trong phòng, presence Online/Offline, Cloudflare R2, Redis hoặc gọi thoại/video.
