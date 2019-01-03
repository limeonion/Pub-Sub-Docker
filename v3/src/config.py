class Config:
    TEST_TOPIC = "test-1"
    IP_ADDRESS_LAST_OCTET_MIN = 2
    IP_ADDRESS_LAST_OCTET_MAX = 20
    IP_ADDRESS_DOCKER_BASE = "172.17.0.2"


class ENDPOINTS:
    SUBSCRIBE = "subscribe"
    PUBLISH = "publish"
    NOTIFY = "notify"


class MIMETYPES:
    APP_JSON = "application/json"


class SERVICE_TYPE:
    TOPIC_BROKER = "topic-broker"
    SUBSCRIBER = "subscriber"
