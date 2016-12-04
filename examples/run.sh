#!/bin/bash

# This script runs the server in production
# Usage: /app/pubsub/examples/run.sh

cd /app/pubsub
. ./venv/bin/activate
exec python server.py
