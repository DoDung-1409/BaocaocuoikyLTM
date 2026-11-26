"""Hàm phát sự kiện Socket.IO dùng chung cho cả HTTP route và socket handler."""
from ..extensions import socketio


def notify_rooms_changed(user_ids):
    """Báo cho mọi thiết bị của các user tải lại danh sách phòng."""
    for uid in set(user_ids):
        socketio.emit("rooms:changed", {}, to=f"user:{uid}")


def broadcast_presence(user_id, is_online, target_user_ids=None):
    """Phát trạng thái Online/Offline của user tới những người liên quan."""
    payload = {
        "user_id": user_id,
        "is_online": is_online,
    }
    if target_user_ids:
        # Gửi riêng cho danh sách user liên quan (ví dụ: người cùng phòng chat)
        for uid in set(target_user_ids):
            if uid != user_id:
                socketio.emit("presence:changed", payload, to=f"user:{uid}")
    else:
        # Hoặc phát toàn hệ thống nếu app của bạn hiển thị trạng thái chung
        socketio.emit("presence:changed", payload)
