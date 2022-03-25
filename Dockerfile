FROM python:3

WORKDIR /paper__bot
COPY . /paper__bot
RUN pip3 install poetry
RUN poetry install
CMD ["poetry", "run", "python", "paper__bot/main.py"]
