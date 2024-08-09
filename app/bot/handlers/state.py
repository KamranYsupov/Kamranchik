import loguru
from aiogram import types, F, Router
from aiogram.filters import StateFilter, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from pydantic import ValidationError
from dependency_injector.wiring import inject, Provide

from core.container import Container
from schemas.resume import ResumeSchema
from services.telegram_user import TelegramUsersService
from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import reply_keyboard_remove

state_router = Router()


class ResumeState(StatesGroup):
    name = State()
    old = State()
    about = State()
    photo = State()


@state_router.message(
    StateFilter('*'),
    or_f(Command('cancel'), (F.text.lower() == '.'))
)
async def cancel_handler(
        message: types.Message,
        state: FSMContext,
):
    await message.answer(
        'Действие отменено',
        reply_keyboard=reply_keyboard_remove
    )
    await state.clear()


@state_router.message(ResumeState.name, F.text)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    if len(name) > 100:
        return await message.answer('Длина именя не должна превышать 100 символов')

    await state.update_data(name=name)
    await state.set_state(ResumeState.old)

    await message.answer(
        'Сколько тебе лет?'
        '\n<em>Отправь "." для отмены</em>',
        parse_mode='HTML'
    )


@state_router.message(ResumeState.old, F.text)
async def process_old(message: types.Message, state: FSMContext):
    old = message.text

    try:
        old = int(old)
        await state.update_data(old=old)
        await state.set_state(ResumeState.photo)
    except ValueError:
        await message.answer('Пожалуйста, введи корректный возраст')
        return

    await message.answer(
        'Отправь свою фотографию'
        '\n<em>Отправь "." для отмены</em>',
        parse_mode='HTML'
    )


@state_router.message(ResumeState.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(ResumeState.about)

    await message.answer(
        'Расскажите немного о себе'
        '\n<em>Отправь "." для отмены</em>',
        parse_mode='HTML')


@state_router.message(ResumeState.about, F.text)
@inject
async def process_about(
        message: types.Message,
        state: FSMContext,
        telegram_users_service: TelegramUsersService = Provide[
            Container.telegram_users_service
        ],
):
    about = message.text
    if len(about) > 500:
        await message.answer('Длина не должна превышать 500 символов')
        return

    await state.update_data(about=about)

    resume_data = await state.get_data()
    resume_schema = ResumeSchema(**resume_data)
    await telegram_users_service.update(
        telegram_id=message.from_user.id,
        obj_in={
            'resume': resume_schema.model_dump()
        }
    )

    profile_message_info = (
            f'<b>Твоя анкета</b>:\n\n'
            + telegram_users_service
            .get_resume_message_info(resume_schema.model_dump())
    )

    await message.answer_photo(
        photo=resume_schema.photo,
        caption=profile_message_info,
        parse_mode='HTML',
        reply_markup=get_inline_keyboard(
            buttons={
                'Просмотр анкет': 'watch_resumes',
                'Изменить 📝': 'update_resume',
                'Удалить 🗑': 'delete_resume',
            }
        ),
    )

    await state.clear()
