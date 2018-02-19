FROM python:3.6-alpine

WORKDIR /usr/src/app

ADD requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "./async_worker.py"]
