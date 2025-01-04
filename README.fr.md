# Monitoring système
[🇬🇧 Read in English](README.md)

## Contexte
Ce code source permet, sur la machine où il est déployé, d'obtenir des informations sur la consommation cpu, mémoire, disque et quelques autres éléments de métrologie pour les publier dans un topic *mqtt* ou tout simplement les afficher sur la *sortie standard*.

## Installation

### Prérequis
Le code proposé ici a été testé sur un raspberry pi 4 modèle B installé avec debian 12.
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
### Procédure d'installation
Le code peut être installé dans un répertoire `scripts/monitoring` d'un utilisateur de la machine, par exemple `/home/pi/scripts/monitoring`. Il est conseillé de créer un environnement virtuel python sous le répertoire `monitoring` puis d'y installer les librairies requises :
```bash
python -m venv env
source /home/pi/scripts/monitoring/env/bin/activate
pip install psutil paho-mqtt
pip freeze > requirements.txt
```

Il faut ensuite créer un fichier `.env_mon` dans ce même répertoire. Il suffit pour cela de s'appuyer sur l'exemple donné par le fichier [env_mon](env_mon) qui peut servir de base. On indiquera notamment l'adresse du broker MQTT (`MQTT_BROKER`) et les éléments de login (`MQTT_USER`, `MQTT_PASSWORD`) ainsi que la localisation du fichier de log (`MON_LOG_FILE`).

## Fonctionnement
Le fichier principal est le programme python [mon.py](mon.py).
Ce dernier utilise la librairie [psutil](https://psutil.readthedocs.io/) pour obtenir des informations sur l'utilisation du système (CPU, memory, disks, network, sensors).

### Invocation en ligne de commande

Pour l'invoquer il faut commencer par activer l'environnement virtuel et "sourcer" le `.env_mon` :  

```bash
pi@rasp39:~/scripts/monitoring $ source /home/pi/scripts/monitoring/env/bin/activate
(env) pi@rasp39:~/scripts/monitoring $ source .env_mon
```

On peut ensuite de demander au programme d'afficher les données à l'écran (option `--no-mqtt`):  
```json
(env) pi@rasp39:~/scripts/monitoring $ python mon.py --no-mqtt
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
````

On peut l'invoquer pour publier sur le topic mqtt (sans paramètre) :  

```bash
(env) pi@rasp39:~/scripts/monitoring $ python mon.py
```

### Intégration dans un crontab

Le fichier [run_mon.sh](run_mon.sh) qui successivement source les variables d'environnement, active l'environnement, exécute le programme python puis désactive l'environnement, a été créé pour pour l'intégration dans le `cron` comme suit :

```bash
(env) pi@rasp39:~/scripts/monitoring $ crontab -l
* * * * * /home/pi/scripts/monitoring/run_mon.sh >> /home/pi/scripts/monitoring/mon.log 2>&1
0 */6 * * * tail -n 100 /home/pi/scripts/monitoring/mon.log > /home/pi/scripts/monitoring/mon.log.tmp && mv /home/pi/scripts/monitoring/mon.log.tmp /home/pi/scripts/monitoring/mon.log
```
La deuxième ligne (`tail  -n 100...`) permet de ne conserver que 100 lignes de log, afin de contenir la taille du fichier.

Une ligne de log ressemble à cela :
```bash
[2025-01-03 14:34:03] Published via MQTT : {"cpu_temperature": 33.1, "cpu_system_usage": 0.2, "cpu_user_usage": 0.0, "cpu_idle_usage": 99.8, "memory_usage_percent": 46.6, "mem_usage_total": 3790.9, "mem_usage_available": 2023.4, "mem_usage_used": 1669.5, "mem_usage_free": 1011.6, "hdd_usage_percent": 1.3, "uptime": "1 day, 16:15:04", "boot_time": "2025-01-01T22:18:59+01:00"}
```
## Requirements
Le script nécessite les bibliothèques Python suivantes :
- `paho-mqtt`
- `psutil`
- toute autre bibliothèque mentionnée dans le fichier `requirements.txt`.

Installez-les à l'aide de pip :

```bash
pip install -r requirements.txt
```

## Métriques
Les données suivantes sont collectées et publiées:

- Pourcentage d'utilisation du processeur.
- Utilisation de la mémoire (utilisée, totale, libre).
- Utilisation du disque (utilisé, total, libre).
- Temps de fonctionnement du système.
- Autres mesures personnalisées configurées dans le script.

## Exemple d'intégration : Home Assistant

En utilisant l'intégration MQTT de Home Assistant on peut créer un appareil correspondant au serveur monitoré et des capteurs pour chacune des métriques. Compléter le fichier de configuration comme suit.
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
Ce projet est placé sous la licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
