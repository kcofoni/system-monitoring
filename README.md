
# System Monitoring
[🇫🇷 Lire en français](README.fr.md)

## About
This source code allows, on the machine where it is deployed, to retrieve information about CPU, memory, disk usage, and some other metrics, and either publish them to an *mqtt* topic or simply display them on the *standard output*.

## Setup

### Prerequisites
The code proposed here has been tested on a raspberry pi 4 model B installed with debian 12.
```bash
pi@rasp39:~ $ cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
NAME="Debian GNU/Linux"
VERSION_ID="12"
VERSION="12 (bookworm)"
VERSION_CODENAME=bookworm
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
``` 
```bash
pi@rasp39:~ $ python3 --version
Python 3.11.2
```
### Installation procedure
The code can be installed in a `scripts/monitoring` directory for a user on the machine, for example `/home/pi/scripts/monitoring`. We recommend creating a virtual python environment under the `monitoring` directory and install the required librairies:
```bash
python -m venv env
source /home/pi/scripts/monitoring/env/bin/activate
pip install psutil paho-mqtt
pip freeze > requirements.txt
```

Next, create a `.env_mon` file in this directory to configure the environment variables needed for the script to function properly. An example is given by the [env_mon](env_mon) file that can be used as a template.

## Usage
The main file is the python script [mon.py](mon.py). The latter uses [psutil](https://psutil.readthedocs.io/) library to obtain information on system usage (CPU, memory, disks, network, sensors).

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
The [run_mon.sh](run_mon.sh) file, which successively sources the environment variables, activates the environment, executes the python program and then deactivates the environment, was created for that:

```bash
(env) pi@rasp39:~/scripts/monitoring $ crontab -l
* * * * * /home/pi/scripts/monitoring/run_mon.sh >> /home/pi/scripts/monitoring/mon.log 2>&1
0 */6 * * * tail -n 100 /home/pi/scripts/monitoring/mon.log > /home/pi/scripts/monitoring/mon.log.tmp && mv /home/pi/scripts/monitoring/mon.log.tmp /home/pi/scripts/monitoring/mon.log
```
The second line (`tail -n 100...`) allows you to keep only 100 log lines, in order to contain the file size.

A log line looks like this:
```bash
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

## Exemple of integration : Home Assistant

Using Home Assistant's MQTT integration, you can create a device corresponding to the server being monitored, and sensors for each metric. Complete your configuration file as illustrated below.
```yaml
mqtt:
  sensor:
    - name: "CPU Temperature"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.cpu_temperature }}"
      unit_of_measurement: "°C"
      device_class: "temperature"
      state_class: "measurement"
      unique_id: "rasp39_cpu_temp"
      device:
        identifiers: "rasp39"
        name: "Raspberry Pi 39"
        manufacturer: "Raspberry Pi Ltd"
        model: "PI4 modèle B"
    - name: "CPU System Usage"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.cpu_system_usage }}"
      unit_of_measurement: "%"
      state_class: "measurement"
      unique_id: "rasp39_cpu_system"
      device:
        identifiers: "rasp39"
    - name: "CPU User Usage"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.cpu_user_usage }}"
      unit_of_measurement: "%"
      state_class: "measurement"
      unique_id: "rasp39_cpu_user"
      device:
        identifiers: "rasp39"
    - name: "CPU Idle Usage"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.cpu_idle_usage }}"
      unit_of_measurement: "%"
      state_class: "measurement"
      unique_id: "rasp39_cpu_idle"
      device:
        identifiers: "rasp39"
    - name: "Memory Usage Percent"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.memory_usage_percent }}"
      unit_of_measurement: "%"
      state_class: "measurement"
      unique_id: "rasp39_memory_usage"
      device:
        identifiers: "rasp39"
    - name: "Memory Total"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.mem_usage_total }}"
      unit_of_measurement: "Mb"
      state_class: "measurement"
      unique_id: "rasp39_memory_total"
      device:
        identifiers: "rasp39"
    - name: "Memory Available"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.mem_usage_available }}"
      unit_of_measurement: "Mb"
      state_class: "measurement"
      unique_id: "rasp39_memory_available"
      device:
        identifiers: "rasp39"
    - name: "Memory Used"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.mem_usage_used }}"
      unit_of_measurement: "Mb"
      state_class: "measurement"
      unique_id: "rasp39_memory_used"
      device:
        identifiers: "rasp39"
    - name: "Memory Free"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.mem_usage_free }}"
      unit_of_measurement: "Mb"
      state_class: "measurement"
      unique_id: "rasp39_memory_free"
      device:
        identifiers: "rasp39"
    - name: "HDD Usage Percent"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.hdd_usage_percent }}"
      unit_of_measurement: "%"
      state_class: "measurement"
      unique_id: "rasp39_hdd_usage"
      device:
        identifiers: "rasp39"
    - name: "Uptime"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.uptime }}"
      unique_id: "rasp39_uptime"
      device:
        identifiers: "rasp39"
    - name: "Boot Time"
      state_topic: "rasp39/system"
      value_template: "{{ value_json.boot_time }}"
      unique_id: "rasp39_boot_time"
      device:
        identifiers: "rasp39"
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
