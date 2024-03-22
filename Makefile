.PHONY: build-api
build-api:
	docker build . -f api.Dockerfile -t api-dev -q

.PHONY: test-db-create
test-db-create:
	docker-compose -f docker-compose-test.yaml up --build -d databasetest

.PHONY: test-api
test-api:test-db-create
	docker-compose -f docker-compose-test.yaml up --build --exit-code-from api-test

# Typecheck api
.PHONY: typecheck-api
typecheck-api: build-api
	docker run -t api-dev pyright

## Run lint api
.PHONY: lint-api
lint-api: build-api
	docker run -t api-dev black --check . --extend-exclude "snapshots|schema"
