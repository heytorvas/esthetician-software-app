import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from db_utils import serialize_for_mongo

class Database:
    _instance: AsyncIOMotorDatabase = None

    @classmethod
    def get_instance(cls) -> AsyncIOMotorDatabase:
        if cls._instance is None:
            mongo_uri = os.getenv("MONGODB_URI")
            db_name = os.getenv("MONGODB_DATABASE")
            client = AsyncIOMotorClient(mongo_uri)
            cls._instance = client.get_database(db_name)
        return cls._instance

def get_database() -> AsyncIOMotorDatabase:
    return Database.get_instance()

# Expose serialize_for_mongo for use in all DB operations
__all__ = ["get_database", "serialize_for_mongo"]
