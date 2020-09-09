FROM python:3.6
WORKDIR /Project/demo

COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt

COPY . .

#CMD echo "" >
CMD python main.py