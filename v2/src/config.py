class Config:
    TOPIC_BROKER_PORT = 7000
    SUBSCRIBER_PORT = 7005
    PUBLISHER_PORT = 7010
    TEST_TOPIC = "test-1"
    BROKER_ADDRESS = "http://localhost:" + str(5000)
    DOCKER_BROKER_ADDRESS = "http://172.17.0.2"


class ENDPOINTS:
    SUBSCRIBE = "subscribe"
    PUBLISH = "publish"
    NOTIFY = "notify"
