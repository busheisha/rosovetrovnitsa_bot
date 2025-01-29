FROM python:3.12

RUN mkdir /app
COPY ./bot /app/bot
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD [“python3”, “./bot/main.py”] 
