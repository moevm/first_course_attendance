import requests
from urllib.parse import urlencode
from logging import getLogger


logger = getLogger()


class PruffmeWrapper:

    URL_STATS = "https://socket-landing04.pruffme.com:443/webinarfullstat/"
    
    
    def __init__(self, session_id, timeout=60):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'sid={session_id}'
        })
        self.timeout = timeout


    def get_webinar_stats(self, webinar, date_from, date_to):
        payload = urlencode({
            'webinar': webinar,
            'date_from': date_from,
            'date_to': date_to,
            'lang': "ru"
        })

        response = self.session.post(self.URL_STATS, data=payload, timeout=self.timeout)
        
        if response.status_code != 200:
            # 404
            # "Wrong user", "Wrong dates", "Wrong webinar"
            logger.error("Error request: %s", response.text)
            return None
        logger.info("Successful request")
        return response.content
    
    
    