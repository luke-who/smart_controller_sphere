#!/usr/bin/python3

#A test file
import requests
import json

endpointurl="http://192.168.1.99/query_status.php"

r=requests.get(endpointurl);
print(r.status_code);
print(r.text)

jsonbody=json.loads(r.text)
print(jsonbody['stopped'])