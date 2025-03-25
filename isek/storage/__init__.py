from isek_config import config
from .file_storage import FileStorage
from .sqlite_storage import SqliteStorage

storage_name = config.get("storage", "enable")
storage = None

if storage_name == "file":
    storage = FileStorage(config.get("storage", "file", "base_dir"))
elif storage_name == "sqlite":
    storage = SqliteStorage(config.get("storage", "sqlite", "base_dir"))
