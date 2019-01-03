import sys
import socket
import hashlib
import requests
import logging
from config import Config, SERVICE_TYPE

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO)


def printe(*kwargs):
    print(*kwargs, file=sys.stdout)
    return


def add_schema_to_url(url: str):
    if not url.startswith("http://"):
        return "http://{0}".format(url)
    else:
        return url


def sysexit(code=1, message=""):
    logging.info("Exiting application {}".format(message))
    sys.exit(code)


def get_current_host_ip():
    """ Gets the current host/containers IP address """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    return sock.getsockname()[0]


def hash_this(message, hash_fn=hashlib.sha512):
    """ Hashes the message string """
    hex = hash_fn(message.encode("utf-8"))
    return hex.hexdigest()


def get_docker_valid_ip_addresses():
    """ Gets the range of IP addresses that docker assigns to the containers on the subnet """
    min_octet = Config.IP_ADDRESS_LAST_OCTET_MIN
    max_octet = Config.IP_ADDRESS_LAST_OCTET_MAX
    base_address = Config.IP_ADDRESS_DOCKER_BASE
    addresses = []
    for last_octet in range(min_octet, max_octet):
        splits = base_address.split(".")
        splits[-1] = str(last_octet)
        addresses.append(".".join(splits))
    return addresses


def poll(url: str):
    """ Pings a URL to see if it is alive """
    try:
        response = requests.get(add_schema_to_url(url), timeout=0.01)
        return response.status_code == 200
    except Exception as e:
        logging.error(e)
    return False


def poll_type(address, service_type=SERVICE_TYPE.TOPIC_BROKER, output_logs=False):
    """ Pings a URL to see if it is alive, and if it corresponds to the type we want """
    try:
        response = requests.get(add_schema_to_url(address), timeout=0.01)
        if response.status_code == 200:
            if response.json()['type'] == service_type:
                return True
    except Exception as e:
        if output_logs:
            logging.error(e)
    return False


def discover(current_host_ip, service_type=SERVICE_TYPE.TOPIC_BROKER, output_logs=False):
    """ Polls all hosts in the docker IP subnet except for a particular host, and compares types """
    addresses = [add_schema_to_url(a) for a in get_docker_valid_ip_addresses() if
                 add_schema_to_url(current_host_ip) != add_schema_to_url(a)]
    valid_hosts = [address for address in addresses if poll_type(address, service_type, output_logs)]
    return valid_hosts
