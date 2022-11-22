FROM python:3.10
WORKDIR /root
COPY . .
ENTRYPOINT ["bash", "deploy.sh"]