# pull official base image
FROM python:3.8-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables : .pyc 파일이 생성되지 않도록 하고, 파이썬 버퍼링 없이 출력
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# 현재 폴더의 내용을 가상 컴퓨터에 복사
COPY . /usr/src/app/

# install dependencies : 최신 pip 업그레이드와 요구된 패키지 리스트를 설치
RUN pip install --upgrade pip
RUN pip install -r requirements.txt