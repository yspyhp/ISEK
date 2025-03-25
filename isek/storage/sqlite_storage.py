import sqlite3


class SqliteStorage(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def load_persona(self, name):
        return {}

    def load_state(self, name):
        return {}