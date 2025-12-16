# pull official base image
FROM python:3.11.2-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
COPY ./requirements-common.txt .
COPY ./api/devsimpy-nogui/requirements-devsimpy-nogui.txt .
COPY ./api/devsimpy-nogui/Domain/requirements-devsimpy-nogui-domain.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
