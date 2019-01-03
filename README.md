# Distributed Systems
Implementing a Pub/Sub messaging system, in the vein of RabbitMQ, Apache Kafka.

## Version 1
This version simply includes a web interface to run a program of your choice, on a Docker container.

## Version 2
This version actually implements the aforementioned pub/sub messaging system.
The model is as follows:
1. We have single, central topic broker, that maintains a list of all subscribers for various topics
2. A publisher that sends messages for a certain topic, to the central broker
3. The topic broker, receives the messages, and forwards them to the subscribers


## Version 3
This version is a modification of Version 2, in that we remove the centralised topic broker,
and replace it with a swarm of distributed topic brokers.

In this case, subscribers subscribe to any topic broker, and publishers publish to any broker. The broker 
that received the message from the publisher, publishes the message to any subscribers it knows of for that topic,
and then passes the message on to the other members of the swarm, who do the same, until every broker in the swarm
has dealt with the message.
