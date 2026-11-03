"""Theo dõi các Socket.IO session để thêm/xóa kết nối khỏi phòng chat.""" 
import threading

_lock = threading.Lock()
_user_sids = {}
_sid_user = {}


def add(user_id, sid, session_key=None):
    with _lock:
        _user_sids.setdefault(user_id, {})[sid] = session_key
        _sid_user[sid] = user_id


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


def sids_for_user(user_id):
    with _lock:
        return list(_user_sids.get(user_id, {}).keys())


def reset():
    with _lock:
        _user_sids.clear()
        _sid_user.clear()
