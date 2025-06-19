# .PHONY is used to tell make the these are commands not files to bypass the checking file logic and imporve the performance speed
.PHONY: venv
venv:
	python -m venv venv

.PHONY: install
install:
	poetry install

.PHONY: install-win-dev

install-win-dev:
	poetry install; pip install dependencies/dlib-19.22.99-cp310-cp310-win_amd64.whl

.PHONY: migrations
migrations:
	poetry run python -m IAS.manage makemigrations

.PHONY: migrate
migrate:
	poetry run python -m IAS.manage migrate

.PHONY: collectstatic
collectstatic:
	poetry run python -m IAS.manage collectstatic --no-input

.PHONY: runserver
runserver:
	poetry run python -m IAS.manage runserver 8080

.PHONY: superuser
superuser:
	poetry run python -m IAS.manage createsuperuser

.PHONY: shell
shell:
	poetry run python -m IAS.manage shell

.PHONY: train-model
train-model:
	poetry run python -m IAS.scripts.train_face_recognization_model

.PHONY: update
update: install migrate;

# Below commands will not work now, we will enable them later
.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: flake8
flake8:
	poetry run flake8

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: docker-up
docker-up:
	test -f .env || touch .env
	docker-compose -f docker-compose.dev.yml up --force-recreate -d prod-db app

.PHONY: docker-down
docker-down:
	docker-compose -f docker-compose.dev.yml down

# PROD
# You should have docker login before running this command
# docker login --username prafulcoder --password <password> --email <email>
.PHONY: docker-prod-build
docker-prod-build:
	docker build -t prafulcoder/ias-app:latest .
	docker push prafulcoder/ias-app:latest

# PROD
.PHONY: docker-prod-up
docker-prod-up:
	docker-compose -f docker-compose.yml up --force-recreate -d prod-db app

.PHONY: docker-prod-down
docker-prod-down:
	docker-compose -f docker-compose.yml down
