#!/bin/bash
echo "Starting 8 Clients"
for i in 1 2 3 4 5 6 7 8
do
    python client.py &
done