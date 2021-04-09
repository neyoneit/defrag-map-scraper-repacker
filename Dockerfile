FROM python:3.8.5

RUN mkdir /wd
COPY src/requirements.txt /
RUN pip install -r /requirements.txt

COPY src/*.py src/alembic.ini /wd/
COPY src/alembic /wd/alembic
COPY src/models /wd/models
COPY src/scrape /wd/scrape
#COPY src/tests /wd/tests
COPY src/ws /wd/ws

ENV PYTHONUNBUFFERED=1
CMD [ "./ws_scrape_once.py" ]
WORKDIR /wd
