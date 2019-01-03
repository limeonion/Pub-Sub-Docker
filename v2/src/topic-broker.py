import os

os.environ['NO_PROXY'] = '127.0.0.1,localhost'

import requests
import logging
from flask import Flask, request, Response
from utils import add_schema_to_url, poll
from config import Config, ENDPOINTS

app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO)


@app.route("/", methods=["GET"])
def local_heartbeat():
    return "Topic Broker - Heartbeat"


class TopicBroker:
    def __init__(self, subscriptions={}):
        self.subscriptions = subscriptions
        self.messages = []
        return

    def notify_all(self, subscribers, topic, message):
        """ Sends the message to all the topic subscribers """
        notified_all = True
        for subscriber in subscribers:
            if not self.notify(subscriber, topic, message):
                notified_all = False
        return notified_all

    def notify(self, subscriber, topic, message):
        """ Sends the message to a subscriber """
        if not poll(subscriber):
            logging.error("Subscriber {0} is down".format(subscriber))
            return False
        url = "{0}/{1}".format(subscriber, ENDPOINTS.NOTIFY)
        cleaned_url = add_schema_to_url(url)
        logging.info("Notifying URL: {}".format(cleaned_url))
        post_data = {'topic': topic, 'data': message}
        logging.info("Message being sent is: {}".format(message))
        response = requests.post(cleaned_url, data=post_data)
        return response.status_code == 200


broker = TopicBroker()


@app.route("/" + ENDPOINTS.PUBLISH + "/<topic>", methods=["POST"])
def publish(topic):
    """ Publish the received message to all known subscribers """
    message = request.get_json()
    if message is None:
        message = request.form['value']
    subscribers = []
    if topic in broker.subscriptions:
        subscribers = broker.subscriptions[topic]
    ret = broker.notify_all(subscribers, topic, message)
    msg, code = "Done", 200
    if not ret:
        msg, code = "Not done", 500
    return Response(msg, status=code)


@app.route("/" + ENDPOINTS.SUBSCRIBE + "/<topic>", methods=["GET"])
def enable_subscription(topic):
    """ Store that a subscriber has asked to be subscribed to a topic """
    remote_addr = add_schema_to_url(request.remote_addr)
    subscriber_address = remote_addr
    logging.debug("Adding subscription for address: {}".format(subscriber_address))
    if topic in broker.subscriptions:
        subscriber_list = broker.subscriptions[topic]
        subscriber_list.append(subscriber_address)
        broker.subscriptions[topic] = list(set(subscriber_list))
    else:
        broker.subscriptions[topic] = [subscriber_address]
    logging.debug("All subscriptions: {}".format(broker.subscriptions))
    return "Success"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
