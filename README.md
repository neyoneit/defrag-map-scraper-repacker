# Map downloader for ws.q3df.org

The script `ws_scrape_once.py` can be run in various environment. You can also use a Docker image, but the image probably brings more benefits for development than for production.

## Configuration

1. Copy src/settings.py.example to src/settings.py.
2. Adjust paths in settings.py if needed.

## Running in Docker

1. Configure the downloader (see above).
2. Adjusting the docker-compose.yml file if needed.
3. Rust run the following command:

        docker-compose up --build

## Running without Docker

### Preparation

1. Configure the downloader (see above).
2. Install Python 3 (tested with 3.8)
3. Install all the requirements:

        pip insttall -r src/requirements.txt

    In some cases, pip uses Python 2. In such case, you might succeed by using pip3 instead:

        pip3 insttall -r src/requirements.txt

### Running

Just run this:

    python src/ws_scrape_once.py

In some cases, this runs Python 2, which is outdated. In such case, you might want to use python3 instead:

    python3 src/ws_scrape_once.py

If you are on Linux, you might want to just call is as a script, as it has the correct hashbang:

        src/ws_scrape_once.py

If you are on Windows and have the correct association of *.py to Python 3 interpreter, you can run it this way:

        src\ws_scrape_once.py

## Using other database than SQlite

The script uses SQLite3 by default. However, if you want to use some other database, it will most likely work as long as it is supported by Alembic.

## Error handling

In many cases, the script rather logs an exception and continues. The rationale behind this is: When there is some unprocessable map pack, it should not block others from being processed. If you don't want the script to behave this way, you can add `--throw-exceptions`. This causes the script to end and not mark the map file as processed.



