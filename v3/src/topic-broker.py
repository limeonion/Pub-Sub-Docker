import os

os.environ['NO_PROXY'] = '127.0.0.1,localhost'

import requests
import logging
import json
from flask import Flask, request, Response
from utils import add_schema_to_url, poll, get_current_host_ip, hash_this, discover
from config import ENDPOINTS, MIMETYPES, SERVICE_TYPE

app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO)

"""
Assumptions:
    1. Currently the message being passed is a single string, everywhere. 
        Whenever you see `message`, it is a string, extracted from the POST request from
        the publisher, from the 'value' field in the JSON
"""


@app.route("/", methods=["GET"])
def advertisement():
    """ Subscriber advertises that it is healthy, and is a 'topic-broker' server """
    response_d = {"message": "Topic Broker Advertisement", "type": SERVICE_TYPE.TOPIC_BROKER}
    return Response(response=json.dumps(response_d), mimetype=MIMETYPES.APP_JSON)


class TopicBroker:
    def __init__(self, subscriptions={}):
        self.subscriptions = subscriptions
        self.messages = {}
        self.allies = []
        self.current_broker_address = ""
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
        # Check if subscruber is alive
        if not poll(subscriber):
            logging.error("Subscriber {0} is down".format(subscriber))
            return False
        # Check if subscriber has already received the same message from this broker
        if broker.has_subscriber_seen_this_message(message, subscriber):
            logging.info(
                "Subscriber {0} has already seen the message {1} so not sending it again to them".format(subscriber,
                                                                                                         message))
            return True
        url = "{0}/{1}".format(subscriber, ENDPOINTS.NOTIFY)
        cleaned_url = add_schema_to_url(url)
        logging.info("Notifying URL: {}".format(cleaned_url))
        post_data = {'topic': topic, 'data': message}
        logging.info("Message being sent is: {}".format(message))
        response = requests.post(cleaned_url, json=post_data)
        notified = response.status_code == 200
        if notified:
            # Update that the subscriber has been sent this message from this broker
            self.update_message_receiver(message, subscriber)
        return notified

    def pass_forward(self, topic, message, origin_chain):
        """ Pass the message along to the remaining hosts in the broker swarm """
        logging.debug("Message: {}, Origin chain: {}".format(message, origin_chain))
        new_orig_chain = list(set(origin_chain + [self.current_broker_address]))
        logging.debug("New Origin chain: {}".format(new_orig_chain))
        ret_array = []
        for ally in self.allies:
            if ally not in new_orig_chain:
                data = {'origin_chain': new_orig_chain, 'value': message}
                formatted_ally_address = "{0}/{1}/{2}".format(add_schema_to_url(ally), ENDPOINTS.PUBLISH, topic)
                logging.info("Passing message {0} to ally {1}".format(data, formatted_ally_address))
                pass_forward_ret = requests.post(formatted_ally_address, json=data)
                ret_array.append(pass_forward_ret)
        return ret_array

    def ping_allies(self):
        """ Make a list of all the other brokers in the broker swarm """
        logging.info("Trying to discover other brokers in the swarm")
        broker_addresses = discover(broker.current_broker_address, SERVICE_TYPE.TOPIC_BROKER)
        # Tell the current broker who its allies are
        self.allies = broker_addresses
        return True

    def update_broker_host_ip(self):
        """ Get the docker assigned IP for this container """
        current_broker_addr = add_schema_to_url(get_current_host_ip())
        if not broker.current_broker_address:
            self.current_broker_address = current_broker_addr
        logging.debug("Current host address: {}".format(current_broker_addr))
        return

    def add_message(self, message):
        self.messages[hash_this(message)] = []
        return

    def update_message_receiver(self, message, receiver):
        key = hash_this(message)
        if key in self.messages:
            self.messages[key].append(receiver)
        else:
            self.messages[key] = [receiver]
        return

    def has_subscriber_seen_this_message(self, message, subscriber):
        key = hash_this(message)
        if key in self.messages:
            receivers = self.messages[key]
            if subscriber in receivers:
                return True
        return False


broker = TopicBroker()


@app.route("/" + ENDPOINTS.PUBLISH + "/<topic>", methods=["POST"])
def publish(topic):
    """
    Publish the received message to all known subscribers,
    and pass it on to the other brokers in the swarm
    """
    try:
        broker.update_broker_host_ip()
        logging.debug("Request JSON: {}".format(request.__dict__))
        broker.ping_allies()
        request_json = request.get_json()
        data = request_json if request_json else request.form
        logging.debug("Publish request data: {}".format(data))
        # This specifies all the brokers that have already dealt with this message
        origin_chain = []
        message = data['value']
        if 'origin_chain' in data:
            origin_chain = data['origin_chain']
        subscribers = []
        if topic in broker.subscriptions:
            subscribers = broker.subscriptions[topic]

        ret = broker.notify_all(subscribers, topic, message)
        pass_forward_ret = broker.pass_forward(topic, message, origin_chain)

        logging.debug("Pass forward return value is: {}".format(pass_forward_ret))

        msg, code = "Done", 200
        if not ret:
            msg, code = "Not done", 500
        return Response(msg, status=code)
    except Exception as e:
        logging.error(e)
        return False


@app.route("/" + ENDPOINTS.SUBSCRIBE + "/<topic>", methods=["GET"])
def enable_subscription(topic):
    """ Store that a subscriber has asked to be subscribed to a topic """
    broker.update_broker_host_ip()
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
    broker.ping_allies()
    # Give the subscriber all the valid brokers
    response_d = {"brokers": broker.allies + [broker.current_broker_address]}
    logging.debug("Sending subscribe response: {}".format(response_d))
    return Response(json.dumps(response_d), mimetype=MIMETYPES.APP_JSON)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
