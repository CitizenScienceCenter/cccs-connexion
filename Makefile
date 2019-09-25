include .env
export

.PHONY: spec swaggerui run
all:
		clean
		start

.PHONY: clean
clean:
		docker-compose -f ${COMPOSE_FILE} rm
		-rm .env

.PHONY: spec
spec:
	  speccy resolve openapi/oapi.yaml -o openapi/cc.yaml

.PHONY: swaggerui
swaggerui:
	docker kill swag
	docker rm swag
	docker run --name=swag -d -e URL="http://localhost:9000/api/v3/openapi.json" -p "5000:8080" swaggerapi/swagger-ui

services: spec swaggerui

local: spec swaggerui run

.PHONY: run
run:
	ENV=config/local.cfg python app.py

.PHONY: test
test:
		ln -sf envs/test.env .env
		docker-compose -f docker-compose.test.yml up --build --force-recreate

.PHONY: start
docker:
		git secret reveal -f
		docker-compose up --build --force-recreate

.PHONY: start_service
daemon:
		git secret reveal -f
		docker-compose -f ${COMPOSE_FILE} up --build --force-recreate -d

.PHONYL: stop
stop:
		docker-compose -f ${COMPOSE_FILE} down
		-rm .env

