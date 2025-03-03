FROM alpine:latest

RUN apk add --no-cache python3 py3-pip
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN mkdir /app
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt

CMD [ "python3", "ingest.py" ]
