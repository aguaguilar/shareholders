import os
from typing import Any, Dict

from pymongo import MongoClient


class ReadOnlyDB:
    """
    Read-only database abstraction. This class was created to abstract the mongodb implementation. So, if you
    in the future want to change to other NO-SQL database you have to only change this class.
    """
    client = None
    database = None
    organization_collection = "organization"

    def __init__(self):
        self.client = MongoClient(
            "mongodb://{user}:{password}@{host}:{port}".format(
                user=os.getenv("MONGO_USER"),
                password=os.getenv("MONGO_PASSWORD"),
                host=os.getenv("MONGO_HOST"),
                port=os.getenv("MONGO_PORT"),
            )
        )
        self.database = self.client[os.getenv("MONGO_DB")]

    def add_new_organization_share(self, data: Dict[str, Any]):
        collection = self.database[self.organization_collection]
        collection.insert_one(data)

    def find_organization_element(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        collection = self.database[self.organization_collection]
        return collection.find_one(spec)

    def find_organizations_element(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        collection = self.database[self.organization_collection]
        return collection.find(spec)

    def update_organization_element(self, spec: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        collection = self.database[self.organization_collection]
        return collection.update(spec, data)
