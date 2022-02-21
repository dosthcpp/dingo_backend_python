#!/bin/bash
concurrently "sudo /usr/bin/python3.8 /home/ubuntu/pm/src/app.py" "node /home/ubuntu/webrtc/index.js"
