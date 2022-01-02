#!/bin/bash

echo "Shutting down..."
python3 launch_recipe.py shutdown.csv
sleep 4
sudo shutdown -h now