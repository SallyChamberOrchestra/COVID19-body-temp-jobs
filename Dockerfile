# for unit test local environment
FROM python:3.7

ADD ./requirements.txt .
RUN pip install -r requirements.txt

ADD tests/test_line.py .
ADD ./line.py .

