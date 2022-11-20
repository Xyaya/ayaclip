FROM python:latest
WORKDIR /root
COPY . .
ENTRYPOINT ["bash", "start.sh"]