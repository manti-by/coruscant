#!/bin/bash
set -a
source /home/manti/www/coruscant/.env
set +a

cd /home/manti/www/coruscant/
/home/manti/www/coruscant/.venv/bin/python -m coruscant.$1
