import loguru
from aiogram import F, Router, types
from aiogram.filters import Command, or_f
from dependency_injector.wiring import inject, Provide

from bot.keyboards.inline import get_inline_keyboard
from core.container import Container
from schemas.telegram_user import TelegramUserSchema
from services.telegram_user import TelegramUsersService
from utils.pagination import Paginator
from utils.likes import LikeEnum, like_handler

like_router = Router()


@like_router.message(
    or_f(
        Command('my_likes'),
        (F.text.casefold() == 'понравившиеся анкеты 💗')
    )
)
@inject
async def my_likes_message_handler(
        message: types.Message,
):
    await like_handler(
        message=message,
        telegram_id=message.from_user.id,
        like_type=LikeEnum.my_likes,
        page_number=1,
    )


@like_router.callback_query(F.data.startswith('my_likes_'))
@inject
async def my_likes_callback_handler(
        callback: types.CallbackQuery,
):
    page_number = int(callback.data.split('_')[-1])
    await like_handler(
        message=callback.message,
        telegram_id=callback.from_user.id,
        like_type=LikeEnum.my_likes,
        page_number=page_number,
    )


@like_router.message(
    or_f(
        Command('liked_by'),
        (F.text.casefold() == 'кому я понравился 💗')
    )
)
@inject
async def liked_by_message_handler(
        message: types.Message,
):
    await like_handler(
        message=message,
        telegram_id=message.from_user.id,
        like_type=LikeEnum.liked_by,
        page_number=1,
    )


@like_router.callback_query(F.data.startswith('liked_by_'))
@inject
async def liked_by_callback_handler(
        callback: types.CallbackQuery,
):
    page_number = int(callback.data.split('_')[-1])
    await like_handler(
        message=callback.message,
        telegram_id=callback.from_user.id,
        like_type=LikeEnum.liked_by,
        page_number=page_number,
    )


@like_router.callback_query(F.data.startswith('like_'))
@inject
async def like_callback_handler(
        callback: types.CallbackQuery,
        telegram_users_service: TelegramUsersService = Provide[
            Container.telegram_users_service
        ],
):
    current_user = await telegram_users_service.get(
        telegram_id=callback.from_user.id
    )
    current_user_schema = TelegramUserSchema(**current_user)
    liked_user_telegram_id = int(callback.data.split('_')[-1])
    liked_user = await telegram_users_service.get(
        telegram_id=liked_user_telegram_id
    )
    liked_user_schema = TelegramUserSchema(**liked_user)

    updated_likes = current_user_schema.my_likes.copy()
    updated_likes.append(liked_user_telegram_id)
    unique_updated_likes_likes = list(set(updated_likes))

    await telegram_users_service.update(
        telegram_id=current_user_schema.telegram_id,
        obj_in={'my_likes': unique_updated_likes_likes},
    )

    updated_liked_by = liked_user_schema.liked_by.copy()
    updated_liked_by.append(current_user_schema.telegram_id)
    unique_updated_liked_by = list(set(updated_liked_by))

    await telegram_users_service.update(
        telegram_id=liked_user_telegram_id,
        obj_in={'liked_by': unique_updated_liked_by},
    )

    if liked_user_telegram_id in current_user_schema.liked_by:
        await callback.bot.send_message(
            text=f'У вас совпадение с @{current_user_schema.username}'
                 f'({current_user_schema.resume.name})!',
            chat_id=liked_user_telegram_id,
        )
        await callback.message.edit_caption(
            caption=f'Свяжитесь с пользователем <em>{liked_user_schema.resume.name}</em> '
                    f'по его username: @{liked_user_schema.username}',
            parse_mode='HTML',
        )
        return
    else:
        await callback.bot.send_photo(
            photo=current_user_schema.resume.photo,
            caption=f'Вы понравились пользователю {current_user_schema.resume.name}!',
            chat_id=liked_user_telegram_id,
            reply_markup=get_inline_keyboard(
                buttons={
                    'Посмотреть профиль': f'resume_{current_user_schema.telegram_id}'
                }
            )
        )

    await callback.message.edit_caption(
        caption=f'Заявка успешно отправлена пользователю {liked_user_schema.resume.name}'
    )
