.PHONY: build-api
build-api:
	docker build . -f api.Dockerfile -t api-dev -q

.PHONY: test-api
test-api: build-api
	docker run -t api-dev pytest --cov -vv

# Typecheck api
.PHONY: typecheck-api
typecheck-api: build-api
	docker run -t api-dev pyright


## Run lint api
.PHONY: lint-api
lint-api: build-api
	docker run -t api-dev black --check . --extend-exclude "snapshots|schema"
