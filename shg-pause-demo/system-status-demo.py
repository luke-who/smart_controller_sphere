#!/usr/bin/python3

#A test file
import requests
import json

# curl http://192.168.1.99/query_status.php 

endpointurl="http://192.168.1.99/query_status.php"
controlshgendpoint="http://192.168.1.99:8161/api/message/SPHERE.CTRL.SHG?type=topic"; 

username='admin';
password='erehps767'
headers = {"Content-Type": "application/json"}

r=requests.get(endpointurl);
print(r.status_code);
print(r.text)

jsonbody=json.loads(r.text)
print(jsonbody['stopped']) 


# START RECORDING PAYLOAD 
# curl -s -u admin:erehps767 -H "Content-Type: application/json" -X POST -d @start-recording-sample.txt http://192.168.1.99:8161/api/message/SPHERE.CTRL.SHG?type=topic 
payload_for_start='{"jsonrpc":"2.0","method":"start","params":{"delay":0, "modality": "all"},"id":"index.php_863310","dest":"node-red","src":"web_wp6"}';  
payload_json=json.loads(payload_for_start);
print(payload_json);
r = requests.post(controlshgendpoint, json=payload_json, auth=(username, password),headers=headers);  
print(r.status_code);  
print(r.text)  

r=requests.get(endpointurl);
print(r.status_code);
print(r.text)

# curl -u admin:erehps767 -H "Content-Type: application/json" -X POST -d @pause-1-hour.txt http://192.168.1.99:8161/api/message/SPHERE.CTRL.SHG?type=topic
payload_for_pause='{"jsonrpc":"2.0","method":"pause","params":{"delay":0, "duration": "1h","modality": "all"},"id":"genie_12345","dest":"node-red","src":"genie"}';
payload_pause_json=json.loads(payload_for_pause);  
r = requests.post(controlshgendpoint, json=payload_pause_json,  auth=(username, password),headers=headers);
print(r.status_code);
print(r.text)

r=requests.get(endpointurl);
print(r.status_code);
print(r.text)
