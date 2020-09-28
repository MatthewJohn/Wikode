#!/bin/bash

docker kill $(docker ps | grep wikode | gawk '{ print $1 }')
./scripts/docker-build.sh
./scripts/docker-run.sh


