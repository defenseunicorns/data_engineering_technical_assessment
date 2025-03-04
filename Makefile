.DEFAULT_GOAL := help

SHELL := /bin/bash

# The current branch name
BRANCH := $(shell git symbolic-ref --short HEAD)
# The "primary" directory
PRIMARY_DIR := $(shell pwd)


# Idiomatic way to force a target to always run, by having it depend on this dummy target
FORCE:

.PHONY: help
help: ## Show available user-facing targets
	grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sed -n 's/^\(.*\): \(.*\)##\(.*\)/\1:\3/p' \
	| column -t -s ":"

.PHONY: help-dev
help-dev: ## Show available dev-facing targets
	grep -E '^_[a-zA-Z0-9_-]+:.*?#_# .*$$' $(MAKEFILE_LIST) \
	| sed -n 's/^\(.*\): \(.*\)#_#\(.*\)/\1:\3/p' \
	| column -t -s ":"

.PHONY: _test-postgres-up
_test-postgres-up: #_# Brings up a postgres container with the correct database / user / password
	docker run \
		--name postgres \
		-p 5432:5432 \
		-e POSTGRES_USER=orders \
		-e POSTGRES_PASSWORD=s3cr3tp455w0rd \
		-e POSTGRES_DB=orders \
		-d \
		postgres:17.4

.PHONY: _test-postgres-down
_test-postgres-down: #_# Brings down the postgres container
	docker stop postgres
	docker remove postgres

.PHONY: _test-schema-up
_test-schema-up: #_# Creates the database schema for psql
	cat ./postgres/schema.sql | docker exec -i postgres psql -U orders -d orders

.PHONY: _test-build-solution
_test-build-solution: #_# Creates the docker image of the solution
	docker build -t solution:latest -f ./src/Dockerfile .
