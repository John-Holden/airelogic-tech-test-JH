# Airelogic-tech-test-John-Holden

## Requirements:
- Docker installed on the host machine
- The `Ocp-Apim-Subscription-Key`, placed inside the `Makefile` env vars - errors will be raised if missing

## Summary:
- The application is run as a docker container to provide consistency across environments
- The application prompts the user for their `surname`, `nhs_number`, & `dob`
- n.b. docker image runs python:bookworm, (i.e. the latest version of Python 3.12.0), and takes advantage of the new standard tomllib module


## Instructions for use:
1. Put the `Ocp-Apim-Subscription-Key` key inside the Makefile `API_KEY` environment variable (line 19 in `Makefile`) 
    - see [here](https://github.com/airelogic/tech-test-portal/blob/main/T2-Lifestyle-Checker/Readme.md#api-details) for more details.
2. From the cli run:
    - `make build`
3. From the cli run:
    - `make exec-it`
4. From inside the container named **airelogic-backend**, run:
    - `python backend.py`


## Improvements:
1. We would run the backend container as a flask application & integrate with a web-based front end
    - this would be simpler to use and not require us to `exec -it` into the container
2. We might want to perform an additional API call to a questions endpoint if the question requirements became `complex.
    - currently we store questions/scoring in a `.toml` file, but this might get messy with a large questionnaire and logic etc. 
3. Custom error/exception messages in various methods, e.g. `validate_input`
4. We could put all constants at the top of the file into a separate config file and read them in during execution.
    - it would help keep the code more concise
5. Modularization: If the script grows any larger, we would breaking the current set of methods into into smaller, more focused functions. 
    - This makes the code easier to maintain and test.
6. Proper unit tests - the code is not tested at all
