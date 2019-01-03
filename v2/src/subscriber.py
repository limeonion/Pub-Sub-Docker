import os

os.environ['NO_PROXY'] = '127.0.0.1,localhost'

import sys
import requests
import logging
from optparse import OptionParser
from flask import Flask, request
from utils import add_schema_to_url, poll, sysexit
from config import Config, ENDPOINTS

app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO)

SUBSCRIBE_TO = Config.DOCKER_BROKER_ADDRESS

subscriber = None
messages = []


@app.route("/", methods=["GET"])
def advertise():
    return "Subscriber - Heartbeat"


class Subscriber:
    def __init__(self, topic: str):
        self.topic = topic
        self.subscriptions = {}
        if self.subscribe(topic):
            logging.info("Successfully subscribed to {0}".format(topic))
        else:
            logging.info("Could not subscribe to {0}".format(topic))
            sysexit()
        return

    def subscribe(self, topic: str):
        """ Subscribe to a topic at the central broker """
        if not poll(SUBSCRIBE_TO):
            logging.error("Broker {0} is down".format(SUBSCRIBE_TO))
            return False
        subscribe_topic = topic if topic else self.topic
        url = add_schema_to_url("{0}/{1}/{2}".format(SUBSCRIBE_TO, ENDPOINTS.SUBSCRIBE, subscribe_topic))
        logging.info("Calling URL {}".format(url))
        response = requests.get(url)
        if response.status_code == 200:
            self.subscriptions[subscribe_topic] = True
        else:
            self.subscriptions[subscribe_topic] = False
        return self.subscriptions[subscribe_topic]


@app.route("/" + ENDPOINTS.NOTIFY, methods=["POST"])
def receive():
    """ Receive the message from the publisher via the broker """
    resp = None
    message = request.get_json()
    if message is None:
        message = request.form
    if message:
        resp = "Received"
    logging.info("Message received: {}".format(message))
    messages.append(message)
    return resp


@app.route("/subscribe-to-new/<topic>", methods=["GET"])
def subscribe_to_new(topic):
    global subscriber
    logging.info("Adding subscription to topic {0}".format(topic))
    subscriber = Subscriber(topic)
    return "Subscribed to {}".format(topic)


def setup_options():
    parser = OptionParser()
    parser.add_option("-t", "--topic", action="store", dest="topic", help="Topic to publish to",
                      default=Config.TEST_TOPIC)
    return parser


if __name__ == "__main__":
    (options, args) = setup_options().parse_args(sys.argv[1:])
    topic = options.topic
    subscriber = Subscriber(topic)
    app.run(host="0.0.0.0", port=80, debug=False)
