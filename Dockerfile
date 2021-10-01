FROM python:3.8 as base

RUN mkdir /API
WORKDIR /API

COPY run.py .
COPY requirements.txt .
COPY config.py .
COPY app ./app
COPY tests ./tests

RUN pip install -r requirements.txt

FROM base as test
CMD ["pytest", "-v"]

FROM base as production
EXPOSE 5000

ENV FLASK_APP run.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]