setup:
	sudo mkdir -p /var/log/coruscant/
	sudo mkdir -p /var/lib/coruscant/
	sudo chown manti:manti /var/log/coruscant/
	sudo chown manti:manti /var/lib/coruscant/
	sqlite3 /var/lib/coruscant/db.sqlite < utils/database.sql

pip:
	uv sync --extra dev

update:
	uv sync --upgrade --extra dev
	uv run pre-commit autoupdate

check:
	git add .
	uv run pre-commit run --all-files

test:
	export LOG_PATH=/tmp/odin.log && cd coruscant/ && uv run pytest

ci: pip check test

deploy:
	scp -r [!.]* coruscant:/home/manti/www/coruscant/
