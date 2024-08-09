from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F
from dependency_injector.wiring import inject, Provide

from handlers.state import ResumeState
from keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import reply_cancel_keyboard, reply_keyboard_remove
from core.container import Container
from schemas.resume import ResumeSchema
from services.telegram_user import TelegramUsersService
from schemas.telegram_user import TelegramUserSchema

resume_router = Router()


@resume_router.callback_query(F.data == 'watch_resumes')
@inject
async def watch_resumes_callback_handler(
        callback: types.CallbackQuery,
        telegram_users_service: TelegramUsersService = Provide[
            Container.telegram_users_service
        ],
):
    telegram_user = await telegram_users_service.get(
        telegram_id=callback.from_user.id
    )
    telegram_user_schema = TelegramUserSchema(**telegram_user)

    pipeline = [
        {'$match': {'telegram_id': {'$nin': telegram_user_schema.watched_resumes}}},
        {'$sample': {'size': 1}}
    ]

    user_to_watch = await telegram_users_service.aggregate(pipeline, one=True)
    if user_to_watch is None:
        return await callback.message.answer('Вы посмотрели все анкеты')

    user_to_watch_telegram_id = user_to_watch['telegram_id']

    resume_message_info = telegram_users_service.get_resume_message_info(
        user_to_watch['resume']
    )

    watched_resumes = telegram_user_schema.watched_resumes.copy()
    watched_resumes.append(user_to_watch_telegram_id)
    unique_watched_resumes = list(set(watched_resumes))

    await telegram_users_service.update(
        telegram_id=telegram_user_schema.telegram_id,
        obj_in={'watched_resumes': unique_watched_resumes}
    )

    await callback.message.answer_photo(
        photo=user_to_watch['resume']['photo'],
        caption=resume_message_info,
        parse_mode='HTML',
        reply_markup=get_inline_keyboard(
            buttons={
                'Отправить заявку 💘': f'like_{user_to_watch_telegram_id}',
                'Следующий ▶': 'watch_resumes',
            }
        ),
    )


@resume_router.callback_query(or_f(F.data == 'update_resume', F.data == 'create_resume'))
async def create_update_resume_callback_handler(
        callback: types.CallbackQuery,
        state: FSMContext,
):
    action_type = callback.data.split('_')[0]
    if action_type == 'create':
        action_message = 'создадим'
    else:
        action_message = 'изменим'

    try:
        await callback.message.edit_caption(
            caption=f'Давай {action_message} тебе анкету. Как тебя зовут?)'
                    '\n<em>Отправь "." для отмены</em>',
            reply_markup=get_inline_keyboard(
                buttons={'Назад 🔙': 'my_resume_edit'}
            ),
            parse_mode='HTML'
        )
    except TelegramBadRequest:
        await callback.message.edit_text(
            f'Давай {action_message} тебе анкету. Как тебя зовут?)'
            '\n<em>Отправь "." для отмены</em>',
            parse_mode='HTML'
        )

    await state.set_state(ResumeState.name)


@resume_router.callback_query(F.data == 'delete_resume')
@inject
async def delete_resume_callback_handler(
        callback: types.CallbackQuery,
        telegram_users_service: TelegramUsersService = Provide[
            Container.telegram_users_service
        ],
):
    await telegram_users_service.update(
        telegram_id=callback.from_user.id,
        obj_in={'resume': None}
    )
    await callback.message.delete()
    await callback.message.answer('Твоя анкета удалена')


@resume_router.callback_query(F.data.startswith('my_resume_'))
@inject
async def my_resume_callback_handler(
        callback: types.CallbackQuery,
        telegram_users_service: TelegramUsersService = Provide[
            Container.telegram_users_service
        ],
):
    telegram_user = await telegram_users_service.get(telegram_id=callback.from_user.id)
    resume_message_info = telegram_users_service.get_resume_message_info(
        telegram_user['resume']
    )

    action_type = callback.data.split('_')[-1]
    bot_action = callback.message.answer_photo \
        if action_type == 'answer' else callback.message.edit_caption

    await bot_action(
        photo=telegram_user['resume']['photo'],
        caption=f'<b>Твоя анкета</b>:\n\n' + resume_message_info,
        parse_mode='HTML',
        reply_markup=get_inline_keyboard(
            buttons={
                'Просмотр анкет': 'watch_resumes',
                'Изменить 📝': 'update_resume',
                'Удалить 🗑': 'delete_resume',
            }
        ),
    )


@resume_router.callback_query(F.data.startswith('resume_'))
@inject
async def resume_callback_handler(
        callback: types.CallbackQuery,
        telegram_users_service: TelegramUsersService = Provide[
            Container.telegram_users_service
        ],
):
    telegram_id = int(callback.data.split('_')[-1])
    telegram_user = await telegram_users_service.get(telegram_id=telegram_id)
    resume_message_info = telegram_users_service.get_resume_message_info(
        telegram_user['resume']
    )

    await callback.message.edit_caption(
        caption=resume_message_info,
        parse_mode='HTML',
        reply_markup=get_inline_keyboard(
            buttons={
                'Принять заявку 💞': f'like_{telegram_id}',
            }
        ),
    )
