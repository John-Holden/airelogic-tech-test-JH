
# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

build:
	docker build -t airelogic-tech-test .


run:
	# Place API KEY below: -e API_KEY={HERE}
	@echo "Running container as deamon..."
	docker run -d --rm --name airelogic-backend \
	-e QCONF_PATH=/etc/QUESTION_CONF.toml \
	-e API_KEY=\
	-e LOGLEVEL=INFO \
	airelogic-tech-test

exec-it:
	@echo "******************************************************"
	@echo "* Run and Execute into a Running Container            *"
	@echo "* User input can be entered here.                    *"
	@echo "*                                                    *"
	@echo "* To run the Python backend, use the following command:*"
	@echo "*                                                    *"
	@echo "*     python backend.py *"
	@echo "*                                                    *"
	@echo "******************************************************"

	$(MAKE) run
	docker exec -it airelogic-backend /bin/bash

stop:
	docker stop airelogic-backend
