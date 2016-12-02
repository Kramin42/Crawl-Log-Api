# Multiple Priority Refreshing Example
The sources are split into two files, `sources_hiprio.yml`,
containing sources for trunk and 0.19 on all servers,
and `sources_lowprio.yml`, containing sources for older versions.

`config.yml` is set to update from `sources_hiprio.yml` every 12 seconds
and from `sources_lowprio.yml` every 2 minutes.
