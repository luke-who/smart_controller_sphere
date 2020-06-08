#!/usr/bin/python



payload_for_pause='{"jsonrpc":"2.0","method":"pause","params":{"delay":0, "duration": "1h","modality": "all"},"id":"genie_12345","dest":"node-red","src":"genie"}';
payload_for_pause_start='{"jsonrpc":"2.0","method":"pause","params":{"delay":0, "duration": "'
payload_for_pause_suffix='","modality": "all"},"id":"genie_12345","dest":"node-red","src":"genie"}';

payloadsample="{\"jsonrpc\":\"2.0\"}";
payloadsample2='{\'jsonrpc\':\'2.0\'}';
payloadsample3="{'jsonrpc':'2.0'}";

pausevalue='1h';
testval=payload_for_pause_start+pausevalue+payload_for_pause_suffix;
print(testval)
