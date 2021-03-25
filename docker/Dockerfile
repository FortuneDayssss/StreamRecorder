
FROM ubuntu:18.04

RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update
RUN apt-get install -y ca-certificates
RUN update-ca-certificates

COPY sources.list /etc/apt/

RUN apt-get -y update
RUN apt-get install -f -y python3-pip nodejs ffmpeg

RUN mkdir -p /src /video /log

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt
