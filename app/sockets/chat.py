"""Xử lý WebSocket (Socket.IO).

Mô hình: mỗi phòng chat = một Socket.IO room tên "room:<id>"; mỗi user có thêm room riêng "user:<id>"
để nhận thông báo cá nhân (đồng bộ nhiều thiết bị). Mọi sự kiện đều kiểm tra lại xác thực và quyền
thành viên ở SERVER, không tin dữ liệu client gửi lên.
"""
from flask import request, session
from flask_login import current_user
from flask_socketio import emit, join_room

from ..extensions import socketio
from ..services import chat_service, room_service
from ..services.errors import ServiceError
from ..services.validation import as_int
from . import presence
from .events import broadcast_presence


@socketio.on("connect")

@socketio.on("connect")
def on_connect(auth=None):
    if not current_user.is_authenticated:
        return False

    uid = current_user.id
    first = presence.add(uid, request.sid, session.get("sk"))

    join_room(f"user:{uid}")

    for rid in room_service.my_room_ids(uid):
        join_room(f"room:{rid}")

    if first:
        broadcast_presence(uid, True)



@socketio.on("presence:request")
def on_presence_request():
    if not current_user.is_authenticated:
        return

    emit("presence:initial", {
        "online_users": presence.online_user_ids()
    })
@socketio.on("disconnect")
def on_disconnect(reason=None):
    uid = presence.remove(request.sid)

    if uid is not None and not presence.sids_for_user(uid):
        broadcast_presence(uid, False)

@socketio.on("message:send")
def on_message_send(data):
    """Trả về dict làm 'ack' cho người gửi. Tin chỉ được phát đi SAU KHI đã lưu DB thành công.""" 
    if not current_user.is_authenticated:
        return {"ok": False, "error": "Phiên đăng nhập đã hết hạn.", "code": 401}
    if not isinstance(data, dict):
        return {"ok": False, "error": "Dữ liệu gửi lên không đúng định dạng.", "code": 400}
    try:
        room_id = as_int(data.get("room_id"), "Phòng")  # từ chối bool/float/None/số âm thay vì ép kiểu lỏng lẻo
        msg, is_new = chat_service.create_text_message(current_user, room_id, data.get("content"),
                                                       data.get("client_msg_id"))
    except ServiceError as exc:
        return {"ok": False, "error": exc.message, "code": exc.status}
    payload = chat_service.serialize_message(msg)
    if is_new:
        emit("message:new", payload, to=f"room:{room_id}")  # tới mọi thành viên, kể cả người gửi
    return {"ok": True, "message": payload}
