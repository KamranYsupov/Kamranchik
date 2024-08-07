from dependency_injector import containers, providers

from repositories.telegram_user import RepositoryTelegramUsers
from services.telegram_user import TelegramUsersService
from mongo.engine import mongo_manager


class Container(containers.DeclarativeContainer):
    # region repository
    repository_telegram_users = providers.Singleton(
        RepositoryTelegramUsers
    )
    # endregion

    # region services
    telegram_users_service = providers.Singleton(
        TelegramUsersService, repository_telegram_users=repository_telegram_users
    )
    # endregion
