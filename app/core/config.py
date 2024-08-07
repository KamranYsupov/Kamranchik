from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки проекта"""

    project_name: str = Field(title='Название проекта')

    # region Настройки бота
    bot_token: str = Field(title='Токен бота')
    # endregion

    # region Настройки БД
    mongo_db_name: str = Field(title='Название БД')
    mongo_initdb_root_username: str = Field(title='Имя пользователя mongo')
    mongo_initdb_root_password: str = Field(title='Пароль пользователя mongo')
    mongo_host: str = Field(default='localhost')
    mongo_port: str = Field(default='27017')
    mongo_default_url: str = Field(
        default='mongodb://{username}:{password}@{host}:{port}/'
    )
    sync_mongo: bool = Field(default=True)
    # endregion

    @property
    def mongodb_url(self):
        return self.mongo_default_url.format(
            username=self.mongo_initdb_root_username,
            password=self.mongo_initdb_root_password,
            host=self.mongo_host,
            port=self.mongo_port,
        )

    class Config:
        env_file = '.env'


settings = Settings()
