import loguru
from aiogram import types

from repositories.telegram_user import RepositoryTelegramUsers
from schemas.telegram_user import TelegramUserSchema
from schemas.resume import ResumeSchema


class TelegramUsersService:
    def __init__(self, repository_telegram_users: RepositoryTelegramUsers):
        self._repository_telegram_users = repository_telegram_users

    async def get(self, **kwargs):
        return await self._repository_telegram_users.get(**kwargs)

    async def aggregate(self, pipeline, one: bool = False):
        result = await self._repository_telegram_users.aggregate(pipeline)
        if not one:
            return result

        try:
            return result[0]
        except IndexError:
            return None

    async def create(self, schema: TelegramUserSchema):
        return await self._repository_telegram_users.create(schema.model_dump())

    async def update(self, *, telegram_id: int, obj_in):
        return await self._repository_telegram_users.update(
            telegram_id=telegram_id,
            obj_in=obj_in,
        )

    async def list(self, **kwargs):
        return self._repository_telegram_users.list(**kwargs)

    @staticmethod
    def get_from_user_formated_data(
            from_user  # message.from_user
    ) -> TelegramUserSchema:
        telegram_user_data = from_user.model_dump()
        telegram_id = telegram_user_data.pop('id')
        telegram_user_data['telegram_id'] = telegram_id
        telegram_user_data['watched_resumes'] = [telegram_id]
        telegram_user_schema = TelegramUserSchema(**telegram_user_data)

        return telegram_user_schema

    @staticmethod
    def get_resume_message_info(resume: dict) -> str:
        resume_schema = ResumeSchema(**resume)

        resume_message_info = (
            f'<b>Имя</b>: <em>{resume_schema.name}</em>\n'
            f'<b>Возраст</b>: <em>{resume_schema.old}</em>\n'
            f'<b>О себе</b>: \n{resume_schema.about}'
        )

        return resume_message_info


    