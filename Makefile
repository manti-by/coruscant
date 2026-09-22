IMAGE := coruscant:latest
PI_IMAGE := coruscant:pi

DOCKER_RUN := docker run --rm \
	-v $(CURDIR):/app \
	-v coruscant-venv:/app/.venv \
	-v coruscant-uv-cache:/root/.cache/uv \
	-v coruscant-pre-commit:/root/.cache/pre-commit \
	-w /app \
	-e LOG_PATH=/tmp/coruscant.log \
	$(IMAGE)

docker-build:
	docker build --tag $(IMAGE) .

docker-build-pi:
	docker build --platform linux/arm/v7 --tag $(PI_IMAGE) .

docker-clean:
	docker rmi $(IMAGE) $(PI_IMAGE) || true
	docker volume rm coruscant-venv coruscant-uv-cache coruscant-pre-commit || true


setup:
	sudo mkdir -p /var/log/coruscant/
	sudo chown manti:manti /var/log/coruscant/

deploy:
	git pull
	uv sync
	sudo service consumer restart


install:
	$(DOCKER_RUN) uv sync --extra dev

update:
	$(DOCKER_RUN) uv run uv-bump
	$(DOCKER_RUN) uv sync --upgrade --extra dev
	$(DOCKER_RUN) uv run pre-commit autoupdate

check:
	$(DOCKER_RUN) uv run pre-commit run --all-files

test:
	$(DOCKER_RUN) uv run pytest coruscant/

ci:
	$(DOCKER_RUN) sh -c "uv sync --extra dev \
		&& uv run pre-commit run --all-files \
		&& uv run pytest coruscant/"
