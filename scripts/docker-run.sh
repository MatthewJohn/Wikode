#!/bin/bash

set -e
set -x

docker run -p 5000:5000 -v $HOME/.ssh:/root/.ssh:ro -v `pwd`/data:/app/data -v `pwd`/config.json:/app/config.json -v `pwd`/db.sqlite:/app/db.sqlite wikode:latest

