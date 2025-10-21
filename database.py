import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class Database:
    _instance: AsyncIOMotorDatabase = None

    @classmethod
    def get_instance(cls) -> AsyncIOMotorDatabase:
        if cls._instance is None:
            client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
            cls._instance = client.get_database("esthetician-app")
        return cls._instance

def get_database() -> AsyncIOMotorDatabase:
    return Database.get_instance()
