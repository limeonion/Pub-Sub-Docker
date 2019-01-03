#!/usr/bin/env bash
port="$1";
function docker_build_and_run {
    if [[ -z ${port} ]]; then
        port="5000";
    fi
    echo "Binding Topic Broker Docker image to $port";
    docker build --file "./Dockerfile.topic-broker" -t pub_sub_docker_v2_topic_broker ./;
    docker run  -p "$port:80" pub_sub_docker_v2_topic_broker;
}

docker_build_and_run;
