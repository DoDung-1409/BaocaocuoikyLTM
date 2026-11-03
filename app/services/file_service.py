"""Các tiện ích kiểm tra và lưu ảnh đại diện (không hỗ trợ gửi file trong phòng chat)."""
import os
import uuid

from flask import current_app

from .errors import ServiceError
from .ratelimit import SlidingWindowLimiter

_avatar_limiter = SlidingWindowLimiter()


def check_upload_rate_limit(user_id):
    allowed, wait = _avatar_limiter.hit(f"avatar:{user_id}", 5, 60)
    if not allowed:
        raise ServiceError(f"Bạn đổi ảnh đại diện quá nhanh. Thử lại sau {wait} giây.", 429,
                          retry_after=wait)


def reset_upload_limits():
    _avatar_limiter.reset()


def validate_avatar(file_storage):
    if file_storage is None or not file_storage.filename:
        raise ServiceError("Bạn chưa chọn ảnh đại diện.")
    ext = os.path.splitext(file_storage.filename)[1].lower().lstrip(".")
    allowed = {"jpg": ("image/jpeg", b"\\xff\\xd8\\xff"),
               "jpeg": ("image/jpeg", b"\\xff\\xd8\\xff"),
               "png": ("image/png", b"\\x89PNG\\r\\n\\x1a\\n"),
               "webp": ("image/webp", None)}
    if ext not in allowed:
        raise ServiceError("Ảnh đại diện chỉ hỗ trợ JPG, PNG hoặc WEBP.")
    mime, signature = allowed[ext]
    stream = file_storage.stream
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    if size <= 0 or size > 2 * 1024 * 1024:
        raise ServiceError("Ảnh đại diện phải có dung lượng từ 1 byte đến 2 MB.", 413)
    head = stream.read(12)
    stream.seek(0)
    valid = head.startswith(signature) if signature else head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if not valid:
        raise ServiceError("Nội dung ảnh không khớp với định dạng.")
    return ext, mime


def delete_keys(keys):
    storage = current_app.extensions["storage"]
    for key in keys:
        try:
            storage.delete(key)
        except Exception:
            current_app.logger.exception("Không xóa được ảnh đại diện cũ")
