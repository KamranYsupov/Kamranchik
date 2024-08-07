FROM python:3.11

WORKDIR /app/

COPY ./pyproject.toml /app/pyproject.toml

COPY ./app /app


RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install

ENV PYTHONPATH=/app

CMD ["python3", "bot/main.py"]
   
