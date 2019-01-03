#!/usr/bin/env bash
docker build -t pub_sub_docker_v1 ./
docker run -p 4000:80 pub_sub_docker_v1
