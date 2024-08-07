from aiogram import F, Router, types
from dependency_injector.wiring import inject, Provide

from core.container import Container
from schemas.telegram_user import TelegramUserSchema
from services.telegram_user import TelegramUsersService

match_router = Router()


@match_router.message(F.data.startswith('💘_'))
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
        telegram_id=liked_user_telegram_id)

    if liked_user_telegram_id in current_user_schema.liked_by:
        await callback.bot.send_message(
            text=f'У вас совпадение с {current_user_schema.username}!',
            chat_id=liked_user_telegram_id,
        )

    updated_likes = current_user['likes'].copy()
    updated_likes.append(liked_user_telegram_id)

    await telegram_users_service.update(
        telegram_id=liked_user_telegram_id,
        obj_in={'likes': updated_likes},
    )

    updated_liked_by = liked_user['liked_by'].copy()
    updated_liked_by.append(current_user.telegram_id)
    await telegram_users_service.update(
        telegram_id=liked_user_telegram_id,
        obj_in={'liked_by': updated_liked_by},
    )
    await callback.message.edit_text(
        f'Заявка успешно отправлена {liked_user}'
    )
