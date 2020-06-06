# python-cache

This code is a little study in caching text in python. This was written while working on code for an API that retrieved text content from a public data service.

I wanted to cache my calls so as to be a good citizen and not put more burden on the public resource than was needed. Initially, because I wanted to focus on the API code, my plan was to use a python dictionary as a simple in-memory key value store. At this point using memcached was overkill, but as it turns out a simple key-value dictionary is underkill.

The problem with just using a dictionary was that 1) it would grow forever and 2) the content becomes stale and needs to expire. This class was written to enable content expiry and to keep the cache within a preset memory footprint.

In the process I learned more about how python uses memory and garbage collection. However, I wouldn't recommend this code to anybody else for production. There are probably bugs, unacceptable assumptions, and it's not a distributed memory cache so it only useful to one process on one server.

Further study around how this code performs with a large number of cached objects is in order.

## Usage
```
import cache

cache = cache.Cache()

```

the rest you'll need to figure out from the code. I used an MD5 hash of the content url as the cache key.

## Demo
```
$python3 -i run.py
>>> r = roundup('sto')
Cache miss: 7b504f1b02a902a597dbe3a2df017f3b
Fetched 4330 bytes of content in 391.29 ms.

>>> r = roundup('sto')
Cache hit: 7b504f1b02a902a597dbe3a2df017f3b
Fetched 4330 bytes of content in 0.06 ms.
``` 