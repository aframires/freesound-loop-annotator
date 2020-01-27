FROM python:3.7

RUN mkdir /code
ADD requirements.txt /code

WORKDIR /code
RUN pip install --no-cache -r requirements.txt

ADD . /code
