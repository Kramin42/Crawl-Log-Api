#!/bin/bash

# This script runs the server in production
# Usage: /app/pubsub/examples/run.sh

cd /app/pubsub
. ./venv/bin/activate
python server.py
exit 0
