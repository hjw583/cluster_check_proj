FROM python:3.6
WORKDIR /Project/demo

COPY requirements.txt ./
RUN /bin/sh -c 'python3 -m pip install -r requirements.txt && apt update && apt install vim -y'

COPY . .

CMD python main.py