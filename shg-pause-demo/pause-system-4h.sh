#!/bin/sh
curl -u admin:erehps767 -H "Content-Type: application/json" -X POST -d @pause-4-hours.txt http://192.168.1.99:8161/api/message/SPHERE.CTRL.SHG?type=topic
