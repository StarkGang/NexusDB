from typing import Any
from core.nexus_collection import  NexusCollection
from sqlite3 import Cursor
import sqlalchemy
from typing import Union


class NexusDatabase:
    def __init__(self, mongo_db: Any, sqlite_db: Any, sql_db: Any):
        self.mongo_db = mongo_db
        self.sqlite_db = sqlite_db
        self.sql_db = sql_db

    def __getattribute__(self, __name: str) -> Any:
        """Returns collection/table object"""
        if self.mongo_db:
            mongo_collection = self.mongo_db[__name]
        return NexusCollection(mongo_collection, self.sqlite_db, self.sql_db)
        

    