# Crawl-Log-Api

## Running
Runs on Python 3.5, install requirements with:

    pip install -r requirements.txt

Then you can start it with:

    python server.py

By default, it loads config_default.yml which is set to download all the files
from servers listed in sources_default.yml. To override this, copy config_default.yml
to config.yml and then edit, linking potentially other sources.yml files.

example production config.yml:

    host: 0.0.0.0
    port: 80
    refresh schedule:
      - sources file: sources_lowprio.yml
        interval: 120
      - sources file: sources_hiprio.yml
        interval: 12

## Web API
The API has one endpoint, `/event`, with optional parameters:
* `limit=<int>`: number of events to return
* `offset=<int>`: event number to start at (returns the `limit` events after `offset`)
* `type=<milestone|game>`: filters to a specific event type
* `src=<src_abbr>`: filters to a specific server
* `reverse`: Returns entries from the most recent. `offset` will be ignored when reverse is used.

A maximum of 1000 events is returned, regardless of `limit`.

e.g.

    /event?type=game&offset=300&limit=100
    /event?src=cpo&reverse

## Realtime Events
Connect to the server with socket.io to receive data of new milestones in reatime.
Example html/js which will add the events to a list as they come in
(replace `http://www.example.com` with the server address):

    <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>
    <script type="text/javascript" charset="utf-8">
        var socket = io.connect('http://www.example.com');
        socket.on('crawlevent', function(data) {
            data = JSON.parse(data);
            data.forEach(function(event) {
                document.getElementById("eventlist").innerHTML+="<li>"+JSON.stringify(event)+"</li>";
            });
        });
    </script>
    <ul id="eventlist"></ul>
