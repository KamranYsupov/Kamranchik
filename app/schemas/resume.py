from pydantic import BaseModel, Field


class ResumeSchema(BaseModel):
    name: str = Field(title='Имя')
    old: int | None = Field(title='Возраст', default=None)
    about: str | None = Field(title='О себе', default=None)
    photo: str | None = Field(title='Фото профиля', default=None)

