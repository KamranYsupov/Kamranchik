from aiogram import Router

from .start import start_router
from .resume import resume_router
from .state import state_router
from .like import like_router


def get_main_router():
    main_router = Router()

    main_router.include_router(start_router)
    main_router.include_router(resume_router)
    main_router.include_router(state_router)
    main_router.include_router(like_router)

    return main_router
