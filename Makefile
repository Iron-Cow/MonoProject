ifneq ($(shell docker compose version 2>/dev/null),)
  DOCKER_COMPOSE=docker compose
else
  DOCKER_COMPOSE=docker-compose
endif


.PHONY: build-api
build-api:
	docker build . -f api.Dockerfile -t api-dev -q

.PHONY: test-db-create
test-db-create:
	$(DOCKER_COMPOSE) -f docker-compose-test.yaml up --build -d databasetest

.PHONY: test-api
test-api:test-db-create
	sleep 10
	$(DOCKER_COMPOSE) -f docker-compose-test.yaml up --build --exit-code-from api-test

# Typecheck api
.PHONY: typecheck-api
typecheck-api: build-api
	docker run -t api-dev pyright -p pyproject.toml

## Run lint api
.PHONY: lint-api
lint-api: build-api
	docker run -t api-dev black --check . --extend-exclude "snapshots|schema"

# Chatbot targets
.PHONY: build-chatbot
build-chatbot:
	docker build chatbot -f chatbot/Dockerfile.dev -t chatbot-dev -q

.PHONY: test-chatbot
test-chatbot: build-chatbot
	docker run -t chatbot-dev pytest -vv

.PHONY: typecheck-chatbot
typecheck-chatbot: build-chatbot
	docker run -t chatbot-dev pyright

.PHONY: lint-chatbot
lint-chatbot: build-chatbot
	docker run -t chatbot-dev black --check src tests
