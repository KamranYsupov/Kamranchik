import random

import loguru
from dependency_injector.wiring import inject, Provide
from aiogram import Router, types
from aiogram.filters import CommandStart, Command

from keyboards.inline import get_inline_keyboard
from core.container import Container
from services.telegram_user import TelegramUsersService
from schemas.telegram_user import TelegramUserSchema
from schemas.resume import ResumeSchema

start_router = Router()


@start_router.message(CommandStart())
@inject
async def start_command_handler(
        message: types.Message,
        telegram_users_service: TelegramUsersService = Provide[
            Container.telegram_users_service
        ],
):
    if not message.from_user.username:
        await message.answer(
            'Перед началом работы '
            'добавьте пожалуйста <em>username</em> в свой телеграм аккаунт'
        )
        return

    buttons = {'Просмотр анкет': 'watch_resumes'}
    telegram_user = await telegram_users_service.get(
        telegram_id=message.from_user.id
    )
    if not telegram_user:
        telegram_user_schema = (
            telegram_users_service.get_from_user_formated_data(
                from_user=message.from_user
            )
        )
        await telegram_users_service.create(telegram_user_schema)
        buttons.update({'Создать анкету': 'create_resume'})
    else:
        if telegram_user.get('resume'):
            buttons.update({'Моя анкета': 'my_resume'})
        else:
            buttons.update({'Создать анкету': 'create_resume'})

    await message.answer(
        text=(f'Привет, @{message.from_user.username}! '
              f'Kamranchik - это бот, в  котором ты сможешь найти свою вторую половинку 💘\n'
              f'Для старта, выбери действие'),
        reply_markup=get_inline_keyboard(
            buttons=buttons
        )
    )


@start_router.message(Command('fake'))
@inject
async def add_fake_user(
        message: types.Message,
        telegram_users_service: TelegramUsersService = Provide[
            Container.telegram_users_service
        ],

):
    fake_user = generate_random_user()

    await telegram_users_service.create(
        schema=fake_user
    )
    await message.answer(
        f'{fake_user.resume.name} успешно создан'
    )


def generate_random_user():
    return TelegramUserSchema(
        telegram_id=random.randint(1, 1000),
        username=f"user_{random.randint(1, 1000)}",
        resume=ResumeSchema(
            name=f"Name{random.randint(1, 100)}",
            old=random.randint(1, 100),
            about='description',
            photo='AgACAgIAAxkBAAJBkWapIgz50kwXsGvgjEZNyy'
                  '5uWqBFAAJG4DEbXpVJSYInRfK387eKAQADAgADeQADNQQ'
        ),
    )
