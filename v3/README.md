# Version 3
## Overview
Version 3 is a modification of version 2's implementation of the pub/sub system.

In this instance, we replace a central topic broker with a swarm of topic brokers. A subscriber can subscribe to a 
topic by informing any topic broker, and a publisher can publish a message for any topic by sending it to any 
broker. The brokers then pass on the message to any subscribers they know are subscribed to that topic, 
and then pass it on to the remaining brokers in the swarm, if any.

The brokers, publishers, and subscribers discover the brokers in the swarm by using a discovery service. This service
uses a advertisement to inform any querying entities about the kind of service they provide, i.e., if they are 
a broker, or a subscriber. This allows the system to be distributed.


## Setup
1. Run the script `src/tb_build_run.sh`. This starts a topic broker, which is accessible at `localhost:5000`. We can 
also specify multiple topic brokers by specifying a port number when running the script, like `bash tb_build_run.sh 5001`
which then brings up a broker accessible at `localhost:5001`
2. Then, run the script `src/sub_build_run.sh`. This starts a subscriber instance, accessible at `localhost:6000`. Optionally, we can specify the port
as well, to create multiple subscriber instances, like `bash sub_build_run.sh 6001`, to start the instance 
and allow it to be accessible at `localhost:6001`
3. We can then run the python 3 script `src/publisher.py` to publish a test message to the topic broker, which in
turn will relay the message to the appropriate subscribers


NOTE: Currently all subscribers subscribe to topic `test-1`, and the publisher also publishes to the same topic. To 
change this behaviour, you will have to modify the variable `SUBSCRIBE_TO` in `src/subscriber.py`, and `publish_to`
in `publisher.py`
