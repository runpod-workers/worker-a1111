#!/bin/bash

# Start the init system
/sbin/init &

python -u /rp_handler.py
