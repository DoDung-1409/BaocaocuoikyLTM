# ConnectHub — Chat nhóm trực tuyến

ConnectHub là ứng dụng web hỗ trợ người dùng tạo phòng, tham gia bằng mã mời và nhắn tin nhóm theo thời gian thực.

## Chức năng
- Đăng ký, đăng nhập và đăng xuất.
- Tạo phòng chat và tham gia phòng bằng mã mời.
- Gửi tin nhắn văn bản thời gian thực qua Socket.IO.
- Lưu và xem lịch sử tin nhắn.
- Xem danh sách thành viên và vai trò chủ phòng.
- Chỉnh sửa thông tin hoặc xóa phòng theo quyền.
- Chat riêng 1-1 (chức năng bổ sung).
- Cập nhật tên hiển thị và ảnh đại diện.

ConnectHub không bao gồm chia sẻ file trong phòng chat, trạng thái Online/Offline, gọi thoại/video hoặc dịch vụ Cloudflare R2/Redis. Ảnh đại diện được lưu trong thư mục local `uploads/`.

## Công nghệ
- Python, Flask, Flask-Login, Flask-SQLAlchemy
- Flask-SocketIO
- SQLite (local), PostgreSQL (nếu cấu hình deploy)
- HTML, CSS, JavaScript
- Git và GitHub

## Chạy trên máy cá nhân
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python run.py
```
Mở `http://127.0.0.1:5000`.

## Cấu hình môi trường
Khi chạy production, đặt `APP_ENV=production` và `SECRET_KEY` an toàn. Có thể đặt `DATABASE_URL` để sử dụng PostgreSQL; nếu không, ứng dụng dùng SQLite tại `instance/connecthub.db`.

## Kiểm thử
```bash
pytest
```

## Repository
Mã nguồn được quản lý bằng Git và GitHub. Trước khi công bố, hãy kiểm tra không commit file `.env`, thông tin mật khẩu hoặc khóa bí mật.
