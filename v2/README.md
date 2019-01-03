# Version 2
## Overview
Version 2 is an implementation of the pub/sub model. 

In this instance, we have a set of publishers, a set of subscribers, and a central topic broker.
The subscribers ask to be subscribed to a topic by informing the topic broker. The publishers
publish messages for any of those topics, by giving them to the topic broker. The topic broker then
match up the subscribers to the topics the publishers have published messages for, and relay them. 

In this manner, neither the subscribers need to know anything about the publishers themselves, nor do the 
publishers need to know anything about the subscribers. The topic broker does all the leg work. 

## Setup
1. Run the script `src/tb_build_run.sh`. This starts the topic broker, which is accessible at `localhost:5000`
2. Then, run the script `src/sub_build_run.sh`. This starts a subscriber instance, accessible at `localhost:6000`. Optionally, we can specify the port
as well, to create multiple subscriber instances, like `bash sub_build_run.sh 6001`, to start the instance 
and allow it to be accessible at `localhost:6001`
3. We can then run the python 3 script `src/publisher.py` to publish a test message to the topic broker, which in
turn will relay the message to the appropriate subscribers


NOTE: Currently all subscribers subscribe to topic `test-1`, and the publisher also publishes to the same topic. To 
change this behaviour, you will have to modify the variable `SUBSCRIBE_TO` in `src/subscriber.py`, and `publish_to`
in `publisher.py`