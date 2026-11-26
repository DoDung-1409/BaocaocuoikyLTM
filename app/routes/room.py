import uuid
import json

from flask import Blueprint, jsonify, request, current_app, send_file
from werkzeug.utils import secure_filename
from ..services import file_service
from ..services.errors import ServiceError
from flask_login import current_user, login_required

from ..extensions import db, socketio
from ..models import Room, RoomMember, User, Message
from ..services import chat_service, room_service
from ..services.validation import as_int, json_dict
from ..sockets import presence
from ..sockets.events import notify_rooms_changed

bp = Blueprint("rooms", __name__, url_prefix="/api")


def _join_sockets(user_id, room_id):
    for sid in presence.sids_for_user(user_id):
        socketio.server.enter_room(sid, f"room:{room_id}")


def _leave_sockets(user_id, room_id):
    for sid in presence.sids_for_user(user_id):
        socketio.server.leave_room(sid, f"room:{room_id}")


def _announce(room, actor, text):
    msg = chat_service.create_system_message(actor, room.id, text)
    if msg:
        socketio.emit("message:new", chat_service.serialize_message(msg), to=f"room:{room.id}")
    socketio.emit("members:changed", {"room_id": room.id}, to=f"room:{room.id}")


@bp.get("/rooms")
@login_required
def list_rooms():
    members = (RoomMember.query.filter_by(user_id=current_user.id).join(Room).order_by(Room.created_at.desc()).all())
    rooms = [room_service.serialize_room_for(current_user, m.room, m) for m in members]
    return jsonify({"rooms": rooms})


@bp.post("/rooms")
@login_required
def create_room():
    data = json_dict()
    room = room_service.create_room(current_user, data.get("name"), data.get("description"))
    _join_sockets(current_user.id, room.id)
    return jsonify({"room": room_service.serialize_room_for(current_user, room)}), 201


@bp.get("/rooms/<int:room_id>")
@login_required
def room_detail(room_id):
    room_service.require_member(current_user, room_id)
    room = db.session.get(Room, room_id)
    data = room_service.serialize_room_for(current_user, room)
    data["members"] = room_service.room_members(room)
    return jsonify({"room": data})


@bp.patch("/rooms/<int:room_id>")
@login_required
def edit_room(room_id):
    data = json_dict()
    room = room_service.update_room(current_user, room_id, data.get("name"), data.get("description"))
    socketio.emit("room:updated", room.to_dict(), to=f"room:{room.id}")
    return jsonify({"room": room_service.serialize_room_for(current_user, room)})


@bp.delete("/rooms/<int:room_id>")
@login_required
def remove_room(room_id):
    room_service.delete_room(current_user, room_id)
    # chỉ báo cho thành viên SAU khi xóa thành công; socket room vẫn còn cho tới khi close_room
    socketio.emit("room:removed", {"room_id": room_id, "reason": "deleted"}, to=f"room:{room_id}")
    socketio.close_room(f"room:{room_id}")
    return jsonify({"ok": True})


@bp.post("/rooms/join")
@login_required
def join_room_by_code():
    data = json_dict()
    room, created = room_service.join_by_code(current_user, data.get("code"))
    _join_sockets(current_user.id, room.id)
    if created:
        _announce(room, current_user, f"{current_user.full_name} đã tham gia phòng")
    notify_rooms_changed([current_user.id])
    return jsonify({"room": room_service.serialize_room_for(current_user, room), "joined": created})


@bp.post("/rooms/<int:room_id>/leave")
@login_required
def leave(room_id):
    room = room_service.leave_room(current_user, room_id)
    _leave_sockets(current_user.id, room_id)
    _announce(room, current_user, f"{current_user.full_name} đã rời phòng")
    notify_rooms_changed([current_user.id])
    return jsonify({"ok": True})



@bp.post("/dm")
@login_required
def open_dm():
    data = json_dict()
    room, other, created = room_service.get_or_create_dm(current_user, data.get("user_id"))
    if created:
        _join_sockets(current_user.id, room.id)
        _join_sockets(other.id, room.id)
        notify_rooms_changed([current_user.id, other.id])
    return jsonify({"room": room_service.serialize_room_for(current_user, room)})


@bp.get("/rooms/<int:room_id>/messages")
@login_required
def messages(room_id):
    room_service.require_member(current_user, room_id)
    args = request.args
    q = (args.get("q") or "").strip()[:100]
    limit = min(max(args.get("limit", type=int) or 30, 1), 100)
    rows, has_more = chat_service.list_messages(room_id, args.get("before_id", type=int),
                                                args.get("after_id", type=int), limit, q or None)
    return jsonify({"messages": [chat_service.serialize_message(m) for m in rows], "has_more": has_more})


@bp.post("/rooms/<int:room_id>/read")
@login_required
def mark_read(room_id):
    last = room_service.mark_read(current_user, room_id, json_dict().get("message_id"))
    return jsonify({"ok": True, "last_read_message_id": last})



@bp.get("/users/search")
@login_required
def search_users():
    q = (request.args.get("q") or "").strip()[:50]
    if len(q) < 2:
        return jsonify({"users": []})
    like = "%" + q.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    users = (User.query.filter(User.id != current_user.id)
             .filter(db.or_(User.username.ilike(like, escape="\\"), User.full_name.ilike(like, escape="\\")))
             .order_by(User.full_name.asc()).limit(10).all())
    return jsonify({"users": [u.to_dict() for u in users]})


@bp.post("/rooms/<int:room_id>/files")
@login_required
def upload_chat_file(room_id):
    room_service.require_member(current_user, room_id)

    uploaded = request.files.get("file")

    ext, mime, size = file_service.validate_chat_file(uploaded)

    filename = secure_filename(uploaded.filename)
    if not filename:
        filename = f"attachment.{ext}"

    storage_key = f"chat/{room_id}/{uuid.uuid4().hex}.{ext}"

    storage = current_app.extensions["storage"]

    try:
        storage.save(storage_key, uploaded.stream, mime)

        msg = chat_service.create_file_message(
            current_user,
            room_id,
            filename,
            storage_key,
            mime,
            size
        )

    except Exception:
        try:
            storage.delete(storage_key)
        except Exception:
            current_app.logger.exception("Lỗi xóa tệp")

        raise

    payload = chat_service.serialize_message(msg)

    socketio.emit(
        "message:new",
        payload,
        to=f"room:{room_id}"
    )

    return jsonify({
        "ok": True,
        "message": payload
    }), 201


@bp.get("/rooms/<int:room_id>/files/<int:message_id>")
@login_required
def download_chat_file(room_id, message_id):
    room_service.require_member(current_user, room_id)

    msg = Message.query.filter_by(
        id=message_id,
        room_id=room_id
    ).first()

    if msg is None or msg.message_type not in ("image", "file"):
        raise ServiceError("Không tìm thấy tệp.", 404)

    try:
        metadata = json.loads(msg.content)
        storage_key = metadata["storage_key"]
        filename = metadata["filename"]
        mime = metadata["mime"]
    except (ValueError, KeyError, TypeError):
        raise ServiceError("Thông tin tệp không hợp lệ.", 500)

    storage = current_app.extensions["storage"]

    try:
        file_obj = storage.open(storage_key)
    except Exception:
        current_app.logger.exception("Lỗi đọc tệp")
        raise ServiceError("Không thể truy cập tệp.", 404)

    response = send_file(
        file_obj,
        mimetype=mime,
       as_attachment=(
    msg.message_type != "image"
    or mime not in ("image/jpeg", "image/png", "image/webp")
    or request.args.get("download") == "1"
),
        download_name=filename,
        max_age=0
    )

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "private, no-store"

    return response
