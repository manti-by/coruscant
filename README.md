# Coruscant IoT module

[![Python 3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://www.python.org/downloads/release/python-3136/)
[![Code style: ruff](https://img.shields.io/badge/ruff-enabled-informational?logo=ruff)](https://astral.sh/ruff)
[![License](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/manti-by/pdw/master/LICENSE)

## About

Raspberry Pi monitoring app, a satellite for [ODIN server](https://github.com/manti-by/odin/)

Author: Alexander Chaika <manti.by@gmail.com>

Source link: https://github.com/manti-by/coruscant/

Requirements:

- Raspberry Pi 2 Model B
- Five DS18B20 sensors
- 10x relays

## Setup python and uv

1. Install [Python 3.13](https://www.python.org/downloads/release/python-3136/) and
create [a virtual environment](https://docs.python.org/3/library/venv.html) for the project.

2. Clone sources, switch to working directory and setup environment:

    ```shell
    git clone https://github.com/manti-by/coruscant.git
    cd coruscant/
    uv sync --all-extras
    ```

3. Install crontabs from utils/crontab.conf

4. Or manually run scripts

    ```shell
    uv run python -m coruscant.sensors
    ```
