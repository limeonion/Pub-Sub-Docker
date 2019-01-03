import os

os.environ['NO_PROXY'] = '127.0.0.1,localhost'
import sys
import requests
import logging
from optparse import OptionParser
from config import Config, ENDPOINTS
from utils import add_schema_to_url, poll

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO)


class Publisher:
    def __init__(self, topic: str):
        self.topic = topic
        return

    def publish(self, message):
        """ Publish message to the central broker """
        publish_to = Config.BROKER_ADDRESS
        # Check if broker is up
        if not poll(publish_to):
            logging.error("Broker {0} is down".format(publish_to))
            return False
        url = add_schema_to_url("{0}/{1}/{2}".format(publish_to, ENDPOINTS.PUBLISH, self.topic))
        logging.info("Publishing to URL {0} : {1}".format(url, message))
        resp = requests.post(url, data=message)
        return resp


def setup_options():
    parser = OptionParser()
    parser.add_option("-m", "--message", action="store", dest="message", help="Message to publish to the subscribers",
                      default="This is a test message for Phase 2 of CSE 586")
    parser.add_option("-t", "--topic", action="store", dest="topic", help="Topic to publish to",
                      default=Config.TEST_TOPIC)
    return parser


if __name__ == "__main__":
    (options, args) = setup_options().parse_args(sys.argv[1:])
    topic = options.topic
    message = options.message
    publisher = Publisher(topic)
    msg_dict = {'value': message}
    logging.info("Sending message {0} for topic {1}".format(msg_dict, topic))
    publisher.publish(msg_dict)
