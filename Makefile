.PHONY: apollo

migrate:
	export PGPASSWORD=apollo
	export SENSORS_MIGRATION_SCRIPT = $(file < utils/create_database.sql)
	psql -h localhost -U apollo apollo -c "$SENSORS_MIGRATION_SCRIPT"

pip:
	uv sync --extra dev

update:
	uv sync --upgrade --extra dev
	pre-commit autoupdate

check:
	git add .
	pre-commit run

test:
	export LOG_PATH=/tmp/odin.log && cd apollo/ && uv run pytest

deploy:
	scp -r [!.]* coruscant:/home/manti/www/apollo/
