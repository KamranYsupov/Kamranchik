from .base import RepositoryBase
from mongo.engine import mongo_manager


class RepositoryTelegramUsers(RepositoryBase):
    """Репозиторий для работы с коллекцией telegram_users"""

    def __init__(self):
        collection = mongo_manager.database['telegram_users']
        super().__init__(collection=collection)

