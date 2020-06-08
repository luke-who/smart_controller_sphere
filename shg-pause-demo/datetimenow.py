#!/usr/bin/python
import datetime
import time

test=datetime.datetime.timestamp(datetime.datetime.now())
print(test);

print(
    datetime.datetime.fromtimestamp(int(test)).strftime('%Y-%m-%d %H:%M:%S')
)

print(time.strftime('%H%M%S',time.localtime()))
