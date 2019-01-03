#!/usr/bin/env bash
port="$1";
function docker_build_and_run {
    if [[ -z ${port} ]]; then
        port="6000";
    fi
    echo "Binding Subscriber Docker image to $port";
    docker build --file "./Dockerfile.subscriber" -t pub_sub_docker_v2_subscriber ./;
    docker run -p "$port:80" pub_sub_docker_v2_subscriber;
}

docker_build_and_run;
