import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import psutil
import json
import argparse
import sys
from datetime import timedelta, datetime, timezone
import paho.mqtt.client as mqtt # type: ignore
import time
from zoneinfo import ZoneInfo  # Used for time zones (Python 3.9+)

# Configuration (default values or environment variables)
# Create an .env_mon file to define the environment variables corresponding
# to the following 6 variables. As a minimum, MQTT_BROKER must be defined,
# MQTT_USER, MQTT_PASSWORD whose default values are not correct.
# To create this .env_mon file, simply rename the env_mon file and add a dot
# after modifying the values to match reality
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker")  # Broker address provided by the environment
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))  # Default port
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "rasp39/system")  # Default topic
MQTT_USER = os.getenv("MQTT_USER", "utilisateur")  # User name provided by environment
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "motdepasse")  # Password provided by environment

def log_message(message):
    """Logs a message to stdout with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_cpu_temperature():
    """Reading CPU temperature via the system file"""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000.0  # Temperature is given in degrees Celsius
        return temp
    except FileNotFoundError:
        return None

def get_uptime():
    """Calculation of operating time and start time with TZ"""
    # Uptime in seconds
    uptime_seconds = time.time() - psutil.boot_time()

    # Calculation of start time in UTC
    boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)

    # Add local time zone
    local_tz = ZoneInfo("Europe/Paris")  # Replace with your time zone
    boot_time_local = boot_time.astimezone(local_tz)

    return {
        "uptime": str(timedelta(seconds=int(uptime_seconds))),
        "boot_time": boot_time_local.isoformat()  # ISO 8601 format with TZ
    }

def get_system_usage():
    """Collects system data and returns a dictionary"""
    # CPU temperature
    cpu_temp = get_cpu_temperature()

    # CPU usage
    cpu_times = psutil.cpu_times_percent(interval=1)
    cpu_system = cpu_times.system
    cpu_user = cpu_times.user
    cpu_idle = cpu_times.idle

    # Memory
    memory_info = psutil.virtual_memory()
    mem_usage_percent = memory_info.percent
    mem_usage_total = memory_info.total
    mem_usage_available = memory_info.available
    mem_usage_used = memory_info.used
    mem_usage_free = memory_info.free

    # Disk
    disk_info = psutil.disk_usage('/')

    # Uptime and start time
    uptime_info = get_uptime()

    # Building data
    data = {
        "cpu_temperature": round(cpu_temp, 2) if cpu_temp else None,
        "cpu_system_usage": round(cpu_system, 2),
        "cpu_user_usage": round(cpu_user, 2),
        "cpu_idle_usage": round(cpu_idle, 2),
        "memory_usage_percent": round(mem_usage_percent, 2),
        "mem_usage_total": round(mem_usage_total/1048576, 1),           # in Mbytes
        "mem_usage_available": round(mem_usage_available/1048576, 1),   # in Mbytes
        "mem_usage_used": round(mem_usage_used/1048576, 1),             # in Mbytes
        "mem_usage_free": round(mem_usage_free/1048576, 1),             # in Mbytes
        "hdd_usage_percent": round(disk_info.percent, 2),
        "uptime": uptime_info["uptime"],
        "boot_time": uptime_info["boot_time"]
    }
    return data

def publish_to_mqtt(json_output):
    """Publishes data to the MQTT broker with authentication if necessary"""
    # Create an MQTT client with the modern version of the protocol
    client = mqtt.Client(protocol=mqtt.MQTTv5)  # Use MQTTv311 if necessary

    # Add authentication if a user/password is provided
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Publish data
    client.publish(MQTT_TOPIC, json_output, retain=True)
    client.disconnect()

def main():
    # Configuring command line arguments
    parser = argparse.ArgumentParser(description="Collect system data and publish via MQTT or display as JSON.")
    parser.add_argument(
        "--no-mqtt",
        action="store_true",
        help="Does not perform MQTT publishing and only displays JSON on stdout."
    )
    args = parser.parse_args()

    # System data collection
    data = get_system_usage()
    json_output = json.dumps(data)

    if args.no_mqtt:
        # Display data in JSON format
        log_message(f"Test mode : JSON generated {json_output}")
    else:
        try:
            # Publish data to MQTT
            publish_to_mqtt(json_output)
            log_message(f"Published via MQTT : {json_output}")
        except Exception as e:
            # Handle exceptions and print to stderr
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] ERROR : {e}", file=sys.stderr)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] CRITICAL ERROR : {e}", file=sys.stderr)