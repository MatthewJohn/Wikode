FROM python:3

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install subversion git --assume-yes && apt-get clean all

COPY .  .

ENTRYPOINT ["bash", "-c", "while true; do FLASK_DEBUG=true python -u ./run.py; sleep 5; done"]

VOLUME /app/data
VOLUME /app/config.json
EXPOSE 5000

