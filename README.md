# Crawl-PubSub

## Running
Runs on Python 3.5, install requirements with:

    pip install -r requirements.txt

Then you can start it with:

    python server.py

By default, it will download all the files from servers listed in sources_default.yml.
To override this, copy sources_default.yml to sources.yml and then edit.

## Web API
The API has one endpoint, `/event`, with optional parameters:
* `limit=<int>`: number of events to return
* `offset=<int>`: event number to start at (returns the `limit` events after `offset`)
* `type=<milestone|game>`: filters to a specific event type

A maximum of 1000 events is returned, regardless of `limit`.

e.g.

    /event?type=game&offset=300&limit=100
