from pydantic import BaseModel, Field

from schemas.resume import ResumeSchema


class TelegramUserSchema(BaseModel):
    telegram_id: int = Field(title='TelegramID пользователя')
    username: str | None = Field(title='Username', default=None)
    resume: ResumeSchema | None = Field(title='Резюме', default=None)
    my_likes: list = Field(title='Понравившиеся', default=[])
    liked_by: list = Field(title='Кому понравился', default=[])
    watched_resumes: list = Field(title='Посмотренные резюме', default=[])
