import requests
from urllib.parse import urlencode
from os import environ
from logging import getLogger

import utils 


logger = getLogger()

URL = "https://socket-landing04.pruffme.com:443/webinarfullstat/"
DATE_FROM = environ.get('WS_DATE_FROM')     # format: "19.10.2024 00:00"
DATE_TO = environ.get('WS_DATE_TO')         # format "19.10.2024 02:00"
WEBINAR_ID = environ.get('WS_WEBINAR_ID')   # id from webinar URL (NOT name)
SESSION_ID = environ.get('WS_SESSION_ID')   # Expires after 360 days from auth
GOOGLE_TOKEN = environ.get("WS_GOOGLE_TOKEN")
TABLE_ID = environ.get("WS_TABLE_ID")
SHEET_NAME = environ.get("WS_SHEET_NAME")


def create_payload():
    return urlencode({
        'webinar': WEBINAR_ID,
        'date_from': DATE_FROM,
        'date_to': DATE_TO,
        'lang': "ru"
    })


def create_headers():
    return {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': f'sid={SESSION_ID}'
    }


def get_stats():
    response = requests.post(
        URL, headers=create_headers(), data=create_payload(), timeout=60)
    if response.status_code != 200:
        # 404
        # "Wrong user", "Wrong dates", "Wrong webinar"
        logger.error("Error request: %s", response.text)
        return None
    logger.info("Successful request")
    return response.content


def main():
    xlsx_file = get_stats()
    if not xlsx_file:
        logger.error("No stats file")
        exit(1)
    
    df = utils.load_sheet_from_table(xlsx_file)
        
    utils.write_data_to_table(df, GOOGLE_TOKEN, TABLE_ID, SHEET_NAME)


if __name__ == "__main__":
    main()
