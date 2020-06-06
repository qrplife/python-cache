# A Class for performing in-memory caching of text objects.
# 
# Why: to reduce traffic to 3rd party services where the text content changes infrequently (~hourly).
# Performance improvement is great side effect.
#
# Requirement 1: ability to stay within a defined a maximum memory footprint.
#
# Requirement 2: ability to expire cached items individually.
# 
import json
import sys
import time
 
class Cache:
    def __init__(self,max_size_kb=100):
        self.cache = {} # The dictionary used to cache the text content.
        self.max_size = max_size_kb * 1024
        self.tidy_trigger_level = int((max_size_kb * 1024) * .8) # Tidy up when we exceed 80% of max size.
        self.tidy_level = int((max_size_kb * 1024) * .5) # Tidy down to 50% of max size so we don't thrash around.
        self.current_size = sys.getsizeof(self.cache)

    def set(self,key,value,ttl=3600):
        expiry = int(time.time())+ttl
        # The cached value is actually a tuple with the text content and an expiry.
        self.cache[key] = (value,expiry)
        self.current_size += (sys.getsizeof(value) + sys.getsizeof(expiry))
        if self.current_size > self.tidy_trigger_level:
            self.tidy()

    def get(self,key):
        if key in self.cache: # Cache hit.
            now = int(time.time())
            # If we are past the expiry then delete the cached tuple and return as a cache miss.
            if now > self.cache[key][1]:
                del(self.cache[key])
                return None
            else:
                return self.cache[key][0] # Not expired, so return the cached text.
        else:
            return None  # Cache miss.

    def tidy(self):
        bytes_to_delete = self.current_size - self.tidy_level
        keys_to_delete = []
        # The expiry value, tuple, and cache dictionary contribution to the overall memory footprint is relatively small.
        # For simplicity let's only count up content bytes for tidying up.
        content_byte_count = 0

        # Delete the oldest first.
        for key in self.cache.keys(): # Iterating over the keys in this way should give us FIFO.
            content_byte_count += sys.getsizeof(self.cache[key][0])
            keys_to_delete.append(key)
            if content_byte_count >= bytes_to_delete:
                break

        # Delete the keys collected. This should remove all refences to the tuple and Python's GC will actually free the memory.
        for key in keys_to_delete:
            del(self.cache[key])

    def getSize(self):
        datasz = 0
        metasz = 0
        dictsz = sys.getsizeof(self.cache)
        keys = self.cache.keys()
        for o in keys:
            datasz += sys.getsizeof(self.cache[o][0])
            metasz += sys.getsizeof(self.cache[o][1])

        report = {
            "data": datasz,
            "meta": metasz,
            "dict": dictsz,
            "total": datasz+metasz+dictsz
        }
        return json.dumps(report)