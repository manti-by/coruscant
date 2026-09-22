setup:
	sudo mkdir -p /var/log/coruscant/
	sudo chown manti:manti /var/log/coruscant/

deploy:
	git pull
	uv sync
	sudo service consumer restart

install:
	uv sync --extra dev

update:
	uv run uv-bump
	uv sync --upgrade --extra dev
	uv run pre-commit autoupdate

check:
	git add .
	uv run pre-commit run --all-files

test:
	export LOG_PATH=/tmp/odin.log && cd coruscant/ && uv run pytest

ci: install check test
