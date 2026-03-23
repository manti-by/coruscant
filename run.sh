#!/bin/bash
cd /home/manti/www/coruscant/
source .env
/home/manti/www/coruscant/.venv/bin/python -m coruscant.$1
