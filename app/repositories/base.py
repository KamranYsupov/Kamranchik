from uuid import UUID
from typing import Generic, Optional, Type, TypeVar

import loguru
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from motor.motor_asyncio import AsyncIOMotorCollection


class RepositoryBase:
    """Репозиторий с базовым CRUD"""
    def __init__(
            self,
            collection: Collection | AsyncIOMotorCollection
    ) -> None:
        self._collection = collection
        self.sync = isinstance(self._collection, Collection)

    async def _async_or_sync_call_query(self, query, *args, **kwargs):
        if self.sync:
            return query(*args, **kwargs)

        return await query(*args, **kwargs)

    async def create(self, data):
        query = self._collection.insert_one
        result = await self._async_or_sync_call_query(query, data)
        return result

    async def get(self, **kwargs) -> dict | None:
        query = self._collection.find_one
        result = await self._async_or_sync_call_query(query, kwargs)
        return result

    async def aggregate(self, pipline) -> list:
        query = self._collection.aggregate
        result = list(await self._async_or_sync_call_query(query, pipline))
        return result

    def list(
            self,
            optional_query: dict | None = None,
            skip: int = None,
            limit: int = None,
            **kwargs
    ) -> list[dict]:

        query = kwargs

        if optional_query:
            query = optional_query

        if skip and limit:
            result = [document for document in self._collection.find(query).skip(skip).limit(limit)]
        else:
            result = [document for document in self._collection.find(query)]

        return result

    async def update(self, *, telegram_id: int, obj_in) -> UpdateResult:
        query = self._collection.update_one
        result = await self._async_or_sync_call_query(
            query,
            {'telegram_id': telegram_id}, {'$set': obj_in}
        )
        return result

    async def delete(self, obj_id: int) -> DeleteResult:
        query = self._collection.delete_one
        result = await self._async_or_sync_call_query(query, {'id': obj_id})
        return result
