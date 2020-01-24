FROM python:3.7

RUN mkdir /app
ADD requirements.txt /app

WORKDIR /app
RUN pip install --no-cache -r requirements.txt

ADD . /app
