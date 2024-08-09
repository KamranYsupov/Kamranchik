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

    async def aggregate(self, pipeline) -> list:
        cursor = self._collection.aggregate(pipeline)

        if self.sync:
            return list(cursor)

        result = [document async for document in cursor]

        return result

    async def list(
            self,
            skip: int = None,
            limit: int = None,
            **kwargs
    ) -> list[dict]:

        if skip and limit:
            cursor = self._collection.find(kwargs).skip(skip).limit(limit)
        else:
            cursor = self._collection.find(kwargs)

        if self.sync:
            result = [document for document in cursor]
        else:
            result = [document async for document in cursor]

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
