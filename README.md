# txstatsd
twisted version for statsd client

to use edit txstatsd.StatsdClient.__init__ method with your statsd server host and port:

```
from txstatsd import statsd

statsd.incr('matric.name')
```
