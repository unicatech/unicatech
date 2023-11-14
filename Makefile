.DEFAULT_GOAL := build
SHELL := /bin/bash
COMPOSE=docker-compose$(COMPOSE_OPTS)
BUILD=up --build -d

DC-FILE=docker-compose.yml
DC=$(COMPOSE) -f $(DC-FILE)

# help: Exibe todos os comandos disponíveis
help:
	@egrep "^# " Makefile

# build: Monta imagens referente ao serviço
build:
	$(DC) --env-file .env $(BUILD)

# down: Desmonta imagens referente ao serviço
down:
	$(DC) down

# restart: Reinicia contâineres referente ao serviço
restart:
	$(DC) restart

drop-db:
	$(COMPOSE) exec db psql -U postgres -c "DROP DATABASE IF EXISTS unicatech;"

create-db-user:
	$(COMPOSE) exec db psql -U postgres -c "DROP USER IF EXISTS unicatech"
	$(COMPOSE) exec db psql -U postgres -c "CREATE USER unicatech WITH PASSWORD 'abelfera';"

create-db:
	$(COMPOSE) exec db psql -U postgres -c "CREATE DATABASE unicatech OWNER unicatech;"
	$(COMPOSE) exec db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE unicatech TO unicatech;"
	$(COMPOSE) exec db psql -U postgres -c "ALTER USER unicatech CREATEDB;"

restore-db:
	@docker cp dump.sql unicatech-db:dump.sql
	$(COMPOSE) exec db bash -c "psql -U postgres -d unicatech < dump.sql"
