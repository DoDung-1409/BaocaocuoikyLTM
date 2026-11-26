
"""Theo dõi các Socket.IO session để quản lý kết nối và trạng thái người dùng."""

import threading

_lock = threading.Lock()
_user_sids = {}
_sid_user = {}


def add(user_id, sid, session_key=None):
    with _lock:
        first = not _user_sids.get(user_id)
        _user_sids.setdefault(user_id, {})[sid] = session_key
        _sid_user[sid] = user_id
        return first


def remove(sid):
    with _lock:
        user_id = _sid_user.pop(sid, None)

        if user_id is None:
            return None

        sids = _user_sids.get(user_id, {})
        sids.pop(sid, None)

        if not sids:
            _user_sids.pop(user_id, None)

        return user_id


def online_user_ids():
    with _lock:
        return list(_user_sids.keys())


def sids_for_user(user_id):
    with _lock:
        return list(_user_sids.get(user_id, {}).keys())


def sids_for_session(session_key):
    if not session_key:
        return []

    with _lock:
        return [
            sid
            for sids in _user_sids.values()
            for sid, key in sids.items()
            if key == session_key
        ]


def reset():
    with _lock:
        _user_sids.clear()
        _sid_user.clear()
