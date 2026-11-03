# Giải thích các kiến thức mạng trong ConnectHub

## HTTP
Trình duyệt gửi request HTTP đến Flask để đăng ký, đăng nhập, tạo phòng và lấy lịch sử tin nhắn. Server trả về response JSON hoặc trang HTML.

## WebSocket và Socket.IO
Chat dùng Flask-SocketIO để duy trì kết nối hai chiều. Người gửi gửi event `message:send`; server kiểm tra đăng nhập và thành viên phòng, lưu tin nhắn vào database rồi phát event `message:new` cho phòng.

## Client–Server
Trình duyệt là Client. Flask là Server. Database lưu thông tin tài khoản, phòng chat, thành viên và tin nhắn. Người dùng không truy cập trực tiếp database.

## Quyền truy cập
Server kiểm tra người dùng có thuộc phòng chat hay không trước khi đọc lịch sử hoặc gửi tin nhắn. Không nên chỉ dựa vào việc ẩn nút trên giao diện.
