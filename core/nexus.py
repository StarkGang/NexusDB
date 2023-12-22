from sqlite3 import connect as sqlite_connect

from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.nexus_database import NexusDatabase
from core.others.custom_exceptions import (
    InvalidMongoURL,
    InvalidPostgreSQLURL,
    InvalidSQLitePath,
)


class NexusClient:
    """Nexus class that takes mongourl, sqlite path, postgreSQL url and returns connected client to client_methods"""

    def __init__(self, mongourl=None, sqlite_path=None, postgreSQL_url=None):
        self.mongourl = mongourl
        self.sqlite_path = sqlite_path
        self.postgreSQL_url = postgreSQL_url

    def initialize(self):
        """Initialize the client"""
        m_client = s_client = p_session = None
        if self.mongourl:
            try:
                m_client = MongoClient(self.mongourl)
                m_client.server_info()
            except Exception as e:
                raise InvalidMongoURL(e)
        if self.sqlite_path:
            try:
                s_client = sqlite_connect(self.sqlite_path).cursor()
            except Exception as e:
                raise InvalidSQLitePath(e)
        if self.postgreSQL_url:
            try:
                p_client = create_engine(self.postgreSQL_url)
                Session = sessionmaker(bind=p_client)
                p_session = Session()
            except Exception as e:
                raise InvalidPostgreSQLURL(e)
        return m_client, s_client, p_session

    def __getattribute__(self, __name: str):
        """Returns database object"""
        mongo_raw_client, sqlite_client, sql_client = self.initialize()
        if mongo_raw_client:
            mongo_db = mongo_raw_client[__name]
        if sqlite_client:
            sqlite_client.execute(f"CREATE DATABASE IF NOT EXISTS {__name}")
            sqlite_client.execute(f"USE {__name}")
            sqlite_db = sqlite_client
        if sql_client:
            sql_client.execute(f"CREATE DATABASE IF NOT EXISTS {__name}")
            sql_client.execute(f"USE {__name}")
            sql_client.commit()
            sql_db = sql_client
        return NexusDatabase(mongo_db, sqlite_db, sql_db)
