.PHONY: create-venv clean-venv test-with-venv-local test-with-venv first-release release lint

INIT_ENVIRONMENT_VARIABLE_SCRIPT=./scripts/load-environment-variables.sh
VENV_ACTIVATE_PATH=venv/bin/activate
APP_FOLDER=app/

# Init new virtual environment
create-venv:
	virtualenv venv --python=python3

# Remove existing virtual environment
clean-venv:
	rm -rf venv

# Test with environment variables saved in .env.local or .env (if .env.local does not exist)
test-with-venv:
	( \
    . ${VENV_ACTIVATE_PATH}; \
    pip3 install -r requirements.txt; \
    . ${INIT_ENVIRONMENT_VARIABLE_SCRIPT}; \
    serverless invoke local -f cron; \
  )

# Run pylint checking
lint:
	( \
    . ${VENV_ACTIVATE_PATH}; \
    pip3 install -r requirements.txt; \
    pylint ${APP_FOLDER} \
  )

# Deploy to AWS lambda
deploy:
	( \
		. ${INIT_ENVIRONMENT_VARIABLE_SCRIPT}; \
		serverless deploy --aws-profile serverless; \
	)

# Create the first release
first-release:
	npx standard-version --first-release

# Create a new release
release:
	npx standard-version
