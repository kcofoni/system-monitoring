
# System Monitoring
[🇫🇷 Lire en français](README.fr.md)

## About
This source code allows, on the machine where it is deployed, to retrieve information about CPU, memory, disk usage, and some other metrics, and either publish them to an *mqtt* topic or simply display them on the *standard output*.

## Setup
The code can be installed in a `scripts/monitoring` directory for a user on the machine, for example `/home/pi/scripts/monitoring`. We recommend creating a virtual python environment under the `monitoring` directory:
```
python -m venv env
```

Next, create a `.env_mon` file in this directory to configure the environment variables needed for the script to function properly. An example is given by the `env_mon` file that can be used as a template.

## Usage
The main file is the python script `mon.pi`. The latter uses [psutil](https://psutil.readthedocs.io/) library to obtain information on system usage (CPU, memory, disks, network, sensors).

### Command line invocation
Before running the script, please activate the *virtual environment* and source the *env* file (`.env_mon`)
as illustrated above:

```bash
source /home/pi/scripts/monitoring/env/bin/activate
source .env_mon
python mon.py --no-mqtt
```
This displays the data on the standard output as shown below:
```json
{
    "cpu_temperature": 34.08,
    "cpu_system_usage": 1.0,
    "cpu_user_usage": 1.0,
    "cpu_idle_usage": 97.0,
    "memory_usage_percent": 43.9,
    "mem_usage_total": 3790.9,
    "mem_usage_available": 2125.1,
    "mem_usage_used": 1567.8,
    "mem_usage_free": 1114.6,
    "hdd_usage_percent": 1.3,
    "uptime": "1 day, 12:03:13",
    "boot_time": "2025-01-01T22:18:59+01:00"
}
```

By default (without any command line parameter), the script transmits information directly to an *mqtt* topic:

```bash
(env) pi@rasp39:~/scripts/monitoring $ python mon.py
```
### Integration within a cron job

You can also configure the script to run periodically using a cron job or a similar scheduling tool.
The `run_mon.sh` file, which successively sources the environment variables, activates the environment, executes the python program and then deactivates the environment, was created for that:

```bash
(env) pi@rasp39:~/scripts/monitoring $ crontab -l
* * * * * /home/pi/scripts/monitoring/run_mon.sh >> /home/pi/scripts/monitoring/mon.log 2>&1
0 */6 * * * tail -n 100 /home/pi/scripts/monitoring/mon.log > /home/pi/scripts/monitoring/mon.log.tmp && mv /home/pi/scripts/monitoring/mon.log.tmp /home/pi/scripts/monitoring/mon.log
```
The second line (`tail -n 100...`) allows you to keep only 100 log lines, in order to contain the file size.

A log line looks like this:
```json
[2025-01-03 14:34:03] Published via MQTT : {"cpu_temperature": 33.1, "cpu_system_usage": 0.2, "cpu_user_usage": 0.0, "cpu_idle_usage": 99.8, "memory_usage_percent": 46.6, "mem_usage_total": 3790.9, "mem_usage_available": 2023.4, "mem_usage_used": 1669.5, "mem_usage_free": 1011.6, "hdd_usage_percent": 1.3, "uptime": "1 day, 16:15:04", "boot_time": "2025-01-01T22:18:59+01:00"}
```
## Configuration
The `.env_mon` file should define the following variables:

- `MQTT_BROKER`: The MQTT broker address.
- `MQTT_PORT`: The port used by the MQTT broker.
- `MQTT_TOPIC`: The topic to which metrics will be published.
- Other environment variables as needed for your specific configuration.

## Requirements
The script requires the following Python libraries:

- `paho-mqtt`
- `psutil`
- Any other libraries mentioned in the `requirements.txt` file.

Install them using pip:

```bash
pip install -r requirements.txt
```

## Metrics
The following metrics are collected and published:

- CPU usage percentage.
- Memory usage (used, total, free).
- Disk usage (used, total, free).
- System uptime.
- Other custom metrics as configured in the script.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
