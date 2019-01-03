import sys
import requests
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO)


def add_schema_to_url(url: str):
    if not url.startswith("http://"):
        return "http://{0}".format(url)
    else:
        return url


def poll(url: str):
    """ Check if host is healthy """
    try:
        response = requests.get(add_schema_to_url(url))
        return response.status_code == 200
    except Exception as e:
        logging.error(e)
        return False


def sysexit(code=1, message=""):
    logging.info("Exiting application {}".format(message))
    sys.exit(code)
