FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /code

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/