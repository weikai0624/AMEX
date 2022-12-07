FROM python:3.8
LABEL maintainer="weikai860624@gmail.com"
RUN apt-get update -qq && apt-get install -y postgresql-client

WORKDIR /AMEX
COPY . /AMEX/

RUN pip install -r requirements.txt

ENTRYPOINT [ "/bin/bash", "docker-entrypoint.sh" ]
