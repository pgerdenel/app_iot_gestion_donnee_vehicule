FROM python:latest
LABEL image-de-base="https://hub.docker.com/_/python"
MAINTAINER My909

RUN pip install paho-mqtt 
RUN pip install xmpppy

## Add the wait script to the image
# ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait
# RUN chmod +x /wait
# CMD ["/wait"]