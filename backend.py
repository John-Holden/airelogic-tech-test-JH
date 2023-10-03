
import re
import os
import tomllib
import requests
import logging
from typing import Tuple
from datetime import datetime

# Min age to use the service
MIN_AGE = 16
# al endpoint 
URL = "https://al-tech-test-apim.azure-api.net/tech-test/t2/patients/"
# Enforced datetime pattern, dd-mm-yyyy. Primarily for patient age.
DT_PATTERN = re.compile(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$')
# NHS id pattern (as given in questionsheet readme, the real one should be 10?)
NHS_NUMBER_PATTERN = re.compile(r'^\d{9}$')
# Score decision boundary - if more than this int patient will be prompted to come in for an appointment
DECISION_BOUND = 3


def get_env(env_name: str) -> str:
    env_val = os.environ.get(env_name)
    if env_val: return env_val
    raise EnvironmentError(f"Missing {env_name}")


# Gets patient age in specific format
def get_dob_dt(dt: str) -> datetime.date:
    try:
        dt = datetime.strptime(dt, '%d-%m-%Y')
    except Exception as e:
        logging.exception(f"[e] Could not convert {dt} to dd-mm-yyyy!")
        raise e
    return dt


# Gets patient age based on dt
def get_patient_age(dt: datetime.date) -> int:
    current_date = datetime.now()
    age = current_date.year - dt.year - ((current_date.month, current_date.day) < (dt.month, dt.day))
    if not age or age > 130:
        raise ValueError("Invalid age!")
        
    return age


def get_q_conf() -> dict:
     # Path to the question config file
    try:
        q_conf: str = get_env("QCONF_PATH") 
        with open(q_conf, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        logging.exception(f"[e] Could read in question conf file. Check the environment is set and the file exists! ")
        raise e


def validate_input(nhs_number: str, surname: str, dob: str) -> None:
    """
        Validation basic user input.
    """

    try:
        assert nhs_number
        assert surname
        assert dob
    except Exception as AssertionError:
        logging.exception(f"[e] Expected non-zero inputs for , surname, and dob. Found: nhs number:'{nhs_number}', surname:'{surname}', dob:'{dob}'")
        raise AssertionError

    try:
        assert NHS_NUMBER_PATTERN.match(nhs_number)
    except Exception as AssertionError:
        logging.exception(f"[e] wrong nhs number input format! Expected 9 consecutive digits. Found {nhs_number}")
        raise AssertionError

    return


def get_patient_details() -> Tuple[str]:
    """
        Collect patient details based on user input.
    """

    nhs_number = input("Enter your nhs number: ")
    surname = input("Enter you surname: ")
    dob = input("Enter your dob (dd-mm-yyyy): ")
    return nhs_number, surname, dob


def validate_req(nhs_number: str, surname: str, input_dob: datetime.date) -> int:
    """
        Validates the nhs_number against surname and dob.
        Returns age of patient.
    """
    
    api_key = get_env("API_KEY")
    resp = requests.get(f"{URL}/{nhs_number}", headers={"Ocp-Apim-Subscription-Key": api_key})
    # Get req data & check status codes
    if resp.status_code == 404:
        logging.exception(f"[e] Your details could not be found!")
        raise requests.exceptions.HTTPError(f"Incorrect response code {resp.status_code}")
    elif resp.status_code != 200:
        logging.exception(f"[e] An error occurred! {nhs_number} : {resp.text}.")
        raise requests.exceptions.HTTPError(f"Incorrect response code {resp.status_code}")  
    
    # Parse req data response for patient.
    try:
        resp = resp.json()
        logging.info(f"[i] Found record for patient: {resp}")
        found_surname, _ = resp["name"].split(',') # last, first names
        found_dob= get_dob_dt(resp["born"])
        age = get_patient_age(found_dob)
    except Exception as e:
        logging.exception(f"[e] Failed to parse name and dob for patient {nhs_number} | {resp}")
        raise e

        # Validate input dob matches the received dob
    if input_dob != found_dob:
        logging.exception(f"[e] Your details could not be found! DOB")
        raise Exception(f"Input dob does not match.")

    # Validate surname match
    if found_surname != surname:
        logging.exception(f"[e] Your details could not be found! SURNAME")
        raise Exception(f"Wrong surname for patient {nhs_number}.")
    
    # Validate min age
    if age < MIN_AGE:
        logging.exception(f"[e] You are not eligible for this service.")
        raise Exception(f"Patient is under {MIN_AGE}.")

    return age


def question_score(question_data: dict, age: int) -> int:
    """
        Get score for patient based on input question dict and user input. 
    """

    try:
        score = 0
        q_index : str
        q_value : dict
        # Iterate through questions conf, depending on yes|no add the correct number of points
        for q_index, q_value in question_data['questions'].items():
            user_input = input(f"{q_value['text']} ").lower()
            
            # null input
            if not user_input:
                raise ValueError("You have to enter text!")

            # format user input
            user_input = user_input[0].upper() + user_input[1:]
            if user_input not in ["Yes", "No"]:
                raise ValueError("Expected either 'Yes' or 'No'!")

            # skip adding points if not applicable - conditional on question & user input
            if not q_value['points'][user_input]:
                logging.info(f"[i] No points to add for patient, skipping.")
                continue
            
            age_range : str
            age_matched = False
            # Iterate through scoring dict to find correct points, break on matching age-range
            for age_range in question_data["scoring"]["AGE"]:
                # Logic for max age bracket
                if len(age_range.split('-')) == 1 and \
                    age > int(age_range[:-1]):
                    age_matched = True
                    break

                lo, hi = map(lambda x : int(x), age_range.split('-'))
                if age > lo and age < hi:
                    age_matched = True
                    break
            
            if not age_matched:
                raise Exception(f"Unable to match age {age} in any range provided in the question conf!")

            score += question_data["scoring"]["AGE"][age_range][q_index]
            logging.info(f"[i] Score updated - {score}")

    except Exception as e:
        logging.exception(f"[e] Error detected when summing the score!")
        raise e
    
    return score


def decision(score: int) -> None:
    """
        output std based on decision logic
    """
    
    if score <= DECISION_BOUND:
        logging.info(" Thank you for answering our questions, we don't need to see you at this time. Keep up the good work!")
        return
        
    logging.info(" We think there are some simple things you could do to improve you quality of life, please phone to book an appointment")
    return


if __name__ == "__main__":

    # Set logging
    log_level = os.environ.get('LOGLEVEL', 'INFO')
    logging.basicConfig(level=log_level)

    # Validate user input and request 
    nhs_number, surname, dob = get_patient_details()
    validate_input(nhs_number, surname, dob)
    validate_req(nhs_number, surname, get_dob_dt(dob))
    score = question_score(question_data=get_q_conf(), age=get_patient_age(get_dob_dt(dob)))
    decision(score)