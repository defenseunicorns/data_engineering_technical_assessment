FROM alpine:latest

RUN apk add --no-cache python3 py3-pip
RUN pip3 install --no-cache --upgrade --break-system-packages pip setuptools

RUN mkdir /app
RUN mkdir /data
RUN mkdir /postgres
COPY ./postgres/schema.sql /postgres
COPY ./data/* /data
COPY ./src/* /app
WORKDIR /app
RUN pip3 install -r requirements.txt --break-system-packages 

CMD [ "python3", "ingest.py" ]
