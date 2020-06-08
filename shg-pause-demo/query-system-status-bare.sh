#!/bin/bash
curl -s http://192.168.1.99/query_status.php | sed -re 's/.*"stopped":(.[^,]*).*/\1/'
echo ""
