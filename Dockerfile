# for unit test local environment
FROM python:3.7

ADD ./requirements.txt .
RUN pip install -r requirements.txt

ADD tests/*.py ./
ADD ./line.py .
ADD ./bigquery.py .
