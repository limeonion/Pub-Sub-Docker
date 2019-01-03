import os

os.environ['NO_PROXY'] = '127.0.0.1,localhost'

import sys
import requests
import logging
import random
import json
from optparse import OptionParser
from flask import Flask, request, Response
from utils import add_schema_to_url, poll, sysexit, discover, get_current_host_ip
from config import Config, ENDPOINTS, MIMETYPES, SERVICE_TYPE

app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO)

subscriber = None
messages = []


# TODO:
# 1. Do not fail if we cannot subscribe to a broker

@app.route("/", methods=["GET"])
def advertisement():
    """ Subscriber advertises that it is healthy, and is a 'subscriber' server """
    response_d = {"message": "Subscriber Advertisement", "type": SERVICE_TYPE.SUBSCRIBER}
    return Response(response=json.dumps(response_d), mimetype=MIMETYPES.APP_JSON)


class Subscriber:
    def __init__(self, topic: str):
        self.topic = topic
        self.subscriptions = {}
        self.brokers = []
        if self.subscribe(topic):
            logging.info("Successfully subscribed to {0}".format(topic))
        else:
            logging.info("Could not subscribe to {0}".format(topic))
            sysexit()
        return

    def subscribe(self, topic: str):
        """ Actually sends the subscription request, by picking a broker at random """
        logging.info("Trying to discover brokers in the swarm")
        brokers = discover(get_current_host_ip(), service_type=SERVICE_TYPE.TOPIC_BROKER)
        # Choose a random broker
        subscribe_to = random.choice(brokers)
        poll_ctr = 0
        while not poll(subscribe_to) and poll_ctr < 5:
            subscribe_to = random.choice(Config.DOCKER_BROKER_ADDRESSES)
            poll_ctr += 1
        logging.info("Subscribing to Host: {0}".format(subscribe_to))
        if not poll(subscribe_to):
            logging.error("Broker {0} is down".format(subscribe_to))
            return False
        # The topic to subscribe to
        subscribe_topic = topic if topic else self.topic
        # Format the url by adding the schema, eg. 'http://' to it
        url = add_schema_to_url("{0}/{1}/{2}".format(subscribe_to, ENDPOINTS.SUBSCRIBE, subscribe_topic))
        logging.info("Calling URL {}".format(url))
        response = requests.get(url)
        response_json = response.json()
        if response_json['brokers']:
            self.brokers = response_json['brokers']
            logging.info("Active brokers: {0}".format(self.brokers))
        if response.status_code == 200:
            self.subscriptions[subscribe_topic] = True
        else:
            self.subscriptions[subscribe_topic] = False
        return self.subscriptions[subscribe_topic]


@app.route("/" + ENDPOINTS.NOTIFY, methods=["POST"])
def receive():
    """ Receives the message from the publisher via the broker """
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
