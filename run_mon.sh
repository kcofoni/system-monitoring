#!/bin/bash

# Load environment variables
source /home/pi/scripts/monitoring/.env_mon

# Activate virtual environment
source /home/pi/scripts/monitoring/env/bin/activate

# Run the Python script
python /home/pi/scripts/monitoring/mon.py

# Deactivate virtual environment
deactivate
