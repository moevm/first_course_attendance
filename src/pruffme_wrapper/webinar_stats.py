import requests
from urllib.parse import urlencode
from os import environ
from logging import getLogger

from pruffme_api import PruffmeWrapper
from utils import load_sheet_from_table, write_data_to_table


logger = getLogger()

DATE_FROM = environ.get('WS_DATE_FROM')     # format: "19.10.2024 00:00"
DATE_TO = environ.get('WS_DATE_TO')         # format "19.10.2024 02:00"
WEBINAR_ID = environ.get('WS_WEBINAR_ID')   # id from webinar URL (NOT name)
SESSION_ID = environ.get('WS_SESSION_ID')   # Expires after 360 days from auth
GOOGLE_TOKEN = environ.get("WS_GOOGLE_TOKEN")
TABLE_ID = environ.get("WS_TABLE_ID")
SHEET_NAME = environ.get("WS_SHEET_NAME")


def main():
    pf = PruffmeWrapper(SESSION_ID)
    xlsx_file = pf.get_webinar_stats(webinar=WEBINAR_ID, date_from=DATE_FROM, date_to=DATE_TO)
    if not xlsx_file:
        logger.error("No stats file")
        exit(1)

    df = load_sheet_from_table(xlsx_file)

    if not write_data_to_table(df, GOOGLE_TOKEN, TABLE_ID, SHEET_NAME):
        logger.error("Error on writing to table")
        exit(1)


if __name__ == "__main__":
    main()
