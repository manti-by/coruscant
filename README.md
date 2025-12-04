# Coruscant IoT module

[![Python3.13](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/downloads/release/python-3112/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/manti-by/Apollo/master/LICENSE)

## About

Raspberry Pi monitoring app, a satellite for [ODIN server](https://github.com/manti-by/odin/)

Author: Alexander Chaika <manti.by@gmail.com>

Source link: https://github.com/manti-by/coruscant/

Requirements:

- Raspberry Pi 2 Model B
- Five DS18B20 sensors
- 10x relays

## Setup Coruscant application

1. Install [Python 3.13](https://www.python.org/downloads/release/python-3136/) and
create [a virtual environment](https://docs.python.org/3/library/venv.html) for the project.

2. Clone sources and install pip packages

```shell
mkdir /home/manti/app/
git clone https://github.com/manti-by/coruscant.git app/
uv sync --all-extras
```

3. Install crontabs from utils/crontab.conf

4. Or run manually scripts

```shell
uv run python -m apollo.sensors
```
