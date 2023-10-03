# Airelogic-tech-test-John-Holden

## T2-Lifestyle-Checker

### Requirements:
- Host machine cli access along with Docker installed
- The `Ocp-Apim-Subscription-Key`, placed inside the `Makefile` env vars - errors will be raised in the application, and when running the docker container if this api key is missing

### Summary:
- The application is run as a docker container to provide consistency across host machine environments
- The application prompts the user for input on their `surname`, `nhs_number`, & `dob`
- n.b: our container runs on top of python:bookworm image, (i.e. the latest version of Python 3.12.0), and takes advantage of the new standard tomllib module

### Instructions for use:
1. Put the `Ocp-Apim-Subscription-Key` key inside the Makefile `API_KEY` env variable (`Makefile` line 19) 
    - see [here](https://github.com/airelogic/tech-test-portal/blob/main/T2-Lifestyle-Checker/Readme.md#api-details) for more details.
    - errors will be raised during the step 3. otherwise
2. From your cli run:
    - `make build`
3. From your cli run:
    - `make exec-it`
4. From inside the container named **airelogic-backend**, run:
    - `python backend.py`
5. To stop the container after you've finished the session, run:
    - `make stop`


### Improvements:
- We would run the backend container as a flask application & integrate with a web-based front end. This would be simpler to use and not require us to `exec -it` into the container or stop the container after execution.
- We might want to perform an additional API call to a separate questions endpoint if the question requirements became complex.
- Currently we store questions/scoring in a `.toml` file, but this might get messy with a large questionnaire. Therefore, we could look to implement a persistent database to house the data. 
- We could implement custom error/exception messages in various methods, e.g. `validate_input`
- All top-level constants could be placed into a separate config file and read them in during execution. Doing so would help keep the code more concise.
- Modularization: If the script grows any larger, we would breaking the current set of methods into into smaller, more focused functions. This makes the code easier to maintain and test.
- Proper unit tests - the code is not tested at all
