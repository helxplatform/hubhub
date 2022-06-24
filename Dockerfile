FROM python:3.9

USER root

RUN apt-get update
RUN apt-get -y install ca-certificates curl gnupg lsb-release

RUN pip install --upgrade pip
RUN pip install PyGithub pyyaml fastapi "uvicorn[standard]"
RUN pip install git+https://github.com/wateim/DockerHub-API.git@master

COPY app /app
COPY ops /app/ops
WORKDIR /app
EXPOSE 9090
CMD uvicorn --host '*' --port 9090 main:app
