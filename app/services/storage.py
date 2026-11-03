"""Lưu trữ cục bộ cho ảnh đại diện người dùng (không dùng dịch vụ cloud)."""
from pathlib import Path


class StorageError(Exception):
    pass


class StorageNotFound(StorageError):
    pass


class StorageUnavailable(StorageError):
    pass


class LocalStorage:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        path = (self.root / key).resolve()
        if self.root not in path.parents:
            raise StorageError("Khóa lưu trữ không hợp lệ")
        return path

    def save(self, key, fileobj, content_type=None):
        path = self._path(key)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as out:
                while True:
                    chunk = fileobj.read(256 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
        except OSError as exc:
            raise StorageUnavailable("Không ghi được vào thư mục lưu trữ") from exc

    def open(self, key):
        path = self._path(key)
        try:
            return open(path, "rb")
        except FileNotFoundError as exc:
            raise StorageNotFound("File không tồn tại") from exc
        except OSError as exc:
            raise StorageUnavailable("Không đọc được thư mục lưu trữ") from exc

    def delete(self, key):
        try:
            self._path(key).unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise StorageUnavailable("Không xóa được file") from exc


def build_storage(config):
    return LocalStorage(config.get("UPLOAD_DIR", "uploads"))
