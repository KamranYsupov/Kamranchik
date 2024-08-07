import pymongo
from motor import motor_asyncio

from core.config import settings


class MongoManager:
    def __init__(
            self,
            db_name: str,
            db_url: str,
            sync: bool = True,
    ):
        self.db_name = db_name
        self.db_url = db_url
        self.sync = sync

    @property
    def db_client(
            self
    ) -> pymongo.MongoClient | motor_asyncio.AsyncIOMotorClient:

        if self.sync:
            return pymongo.MongoClient(self.db_url)
        return motor_asyncio.AsyncIOMotorClient(self.db_url)

    @property
    def database(self):
        return self.db_client[self.db_name]

    def drop_database(self) -> None:
        self.db_client.drop_database(self.db_name)


mongo_manager = MongoManager(
    db_name=settings.mongo_db_name,
    db_url=settings.mongodb_url,
    sync=settings.sync_mongo
)

