FROM python:3.12.2
WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
COPY . /bot
CMD python bot.py