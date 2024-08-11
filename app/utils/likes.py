import enum

import loguru
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputMediaPhoto
from dependency_injector.wiring import inject, Provide

from bot.keyboards.inline import get_inline_keyboard
from core.container import Container
from schemas.telegram_user import TelegramUserSchema
from services.telegram_user import TelegramUsersService
from .pagination import Paginator


class LikeEnum(enum.Enum):
    my_likes = 'my_likes'
    liked_by = 'liked_by'


@inject
async def like_handler(
        message: types.Message,
        telegram_id: int,
        page_number: int,
        like_type: LikeEnum,
        telegram_users_service: TelegramUsersService = Provide[
            Container.telegram_users_service
        ],
):
    telegram_user = await telegram_users_service.get(
        telegram_id=telegram_id
    )
    telegram_user_schema = TelegramUserSchema(**telegram_user)

    if like_type == LikeEnum.my_likes:
        kwargs = {'telegram_id': {'$in': telegram_user_schema.my_likes}}
        callback_prefix = LikeEnum.my_likes.value
        empty_message = 'Вы не лайкнули ни одного пользователя!'
    else:
        kwargs = {'telegram_id': {'$in': telegram_user_schema.liked_by}}
        callback_prefix = LikeEnum.liked_by.value
        empty_message = 'Вы пока никому не понравились('

    like_list = await telegram_users_service.list(**kwargs)
    if not like_list:
        await message.answer(empty_message)
        return

    paginator = Paginator(like_list, page_number=page_number)

    if len(paginator.get_page()):
        user = paginator.get_page()[0]
        user_telegram_id = user['telegram_id']
        message_text = telegram_users_service.get_resume_message_info(
            resume=user['resume']
        )

        if like_type == LikeEnum.liked_by \
                and user_telegram_id not in telegram_user_schema.my_likes:
            buttons = {'Принять заявку 💞': f'like_{user_telegram_id}'}
            sizes = (1, 2)
        else:
            buttons = dict()
            sizes = (2,)

        if paginator.has_previous():
            buttons |= {'◀ Пред.': f'{callback_prefix}_{page_number - 1}'}
        if paginator.has_next():
            buttons |= {'След. ▶': f'{callback_prefix}_{page_number + 1}'}

        message_data = dict(
            caption=message_text,
            reply_markup=get_inline_keyboard(
                buttons=buttons, sizes=sizes
            ),
            parse_mode='HTML'
        )
        media = InputMediaPhoto(
            media=user['resume']['photo'],
            **message_data


        )
        try:

            await message.edit_media(
                media=media,
                **message_data
            )
        except TelegramBadRequest:
            await message.answer_photo(
                photo=media.media,
                **message_data,
            )

