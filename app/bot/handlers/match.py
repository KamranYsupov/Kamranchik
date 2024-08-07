from aiogram import F, Router, types
from dependency_injector.wiring import inject, Provide

from bot.keyboards.inline import get_inline_keyboard
from core.container import Container
from schemas.telegram_user import TelegramUserSchema
from services.telegram_user import TelegramUsersService

match_router = Router()


@match_router.callback_query(F.data.startswith('💘_'))
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

    updated_likes = current_user_schema.my_likes.copy()
    updated_likes.append(liked_user_telegram_id)

    await telegram_users_service.update(
        telegram_id=current_user_schema.telegram_id,
        obj_in={'my_likes': updated_likes},
    )

    updated_liked_by = liked_user['liked_by'].copy()
    updated_liked_by.append(current_user_schema.telegram_id)
    await telegram_users_service.update(
        telegram_id=liked_user_telegram_id,
        obj_in={'liked_by': updated_liked_by},
    )

    if liked_user_telegram_id in current_user_schema.liked_by:
        await callback.bot.send_message(
            text=f'У вас совпадение с @{current_user_schema.username}!',
            chat_id=liked_user_telegram_id,
        )
    else:
        await callback.bot.send_message(
            text=f'Вы понравились пользователю @{current_user_schema.username}!',
            chat_id=liked_user_telegram_id,
            reply_markup=get_inline_keyboard(
                buttons={
                    'Посмотреть профиль': f'resume_{current_user_schema.telegram_id}'
                }
            )
        )

    liked_user_name = liked_user['resume']['name']
    await callback.message.answer(
        f'Заявка успешно отправлена пользователю {liked_user_name}'
    )


@match_router.callback_query(F.data.startswith('💞_'))
@inject
async def match_callback_handler(
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

    updated_likes = current_user_schema.my_likes.copy()
    updated_likes.append(liked_user_telegram_id)

    await telegram_users_service.update(
        telegram_id=current_user_schema.telegram_id,
        obj_in={'my_likes': updated_likes},
    )

    updated_liked_by = liked_user['liked_by'].copy()
    updated_liked_by.append(current_user_schema.telegram_id)
    await telegram_users_service.update(
        telegram_id=liked_user_telegram_id,
        obj_in={'liked_by': updated_liked_by},
    )

    if liked_user_telegram_id in current_user_schema.liked_by:
        await callback.bot.send_message(
            text=f'У вас совпадение с @{current_user_schema.username}!',
            chat_id=liked_user_telegram_id,
        )
    else:
        await callback.bot.send_message(
            text=f'Вы понравились пользователю {current_user_schema.resume.name}!',
            chat_id=liked_user_telegram_id,
            reply_markup=get_inline_keyboard(
                buttons={
                    'Посмотреть профиль': f'resume_{current_user_schema.telegram_id}'
                }
            )
        )

    liked_user_name = liked_user['resume']['name']
    await callback.message.answer(
        f'Заявка успешно отправлена пользователю {liked_user_name}'
    )