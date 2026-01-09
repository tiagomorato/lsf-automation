import os
import logging
import time
from typing import List, Tuple
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

load_dotenv()

def driver_wait_until(by: By, input: str) -> WebElement:
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((by, input)))

def login(driver: WebDriver, login_url: str, username: str, password: str) -> bool:
    """
    Logs into a website using the provided credentials.

    Parameters:
        driver (webdriver): The Selenium WebDriver instance.
        login_url (str): The URL of the login page.
        username (str): The username or email for login.
        password (str): The password for login.
    """

    driver.get(login_url)
    try:
        username_field = driver_wait_until(By.ID, "asdf")
        username_field.clear()
        username_field.send_keys(username)

        password_field = driver_wait_until(By.ID, "fdsauhi")
        password_field.clear()
        password_field.send_keys(password)

        login_button = driver_wait_until(By.ID, "loginForm:login")
        login_button.click()

        logging.getLogger("lsf_automation").info("Logged in successfully.")
        return True
    except Exception as e:
        logging.getLogger("lsf_automation").exception(f"Login failed: {e}")
        return False

def setup_logging() -> Tuple[logging.Logger, str]:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILENAME = os.path.join(LOG_DIR, f"lsf_automation_{LOG_TIMESTAMP}.log")

    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILENAME, encoding="utf-8"),
        ],
    )

    logger = logging.getLogger("lsf_automation")
    return logger, LOG_FILENAME

def init_driver(headless: bool = True) -> WebDriver:
    options = Options()
    if headless:
        options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver


def fetch_table_data(driver: WebDriver, pattern: str = "Notenspiegel") -> List[Tuple[str, ...]]:
    a_element = driver.find_element(By.XPATH, f"//a[contains(text(), '{pattern}')]")
    a_element.click()

    table = driver.find_element(By.XPATH, "//*[@id='wrapper']/div[6]/div[2]/form/table")
    rows = table.find_elements(By.XPATH, ".//tr")
    data = []

    for row in rows:
        cells = row.find_elements(By.XPATH, ".//td")
        all_data = [cell.text for cell in cells]

        if all_data:
            data.append(tuple(all_data))

    return data

def process_and_log_data(data: List[Tuple[str, ...]], logger: logging.Logger) -> None:
    if not data:
        logger.info("No table data found.")
        return

    all_grades = []
    all_points = []

    longest = [name[1] for name in data]
    longest = [name.split("/\n")[1].strip() for name in longest if "/\n" in name]
    if not longest:
        logger.info("No entries with expected format found in data.")
        return

    max_len = max(len(name) for name in longest)

    for item in data:
        if "/\n" in item[1]:
            bezeichnung = item[1].split("/\n")[1].strip()
            note = item[2]

            # if there is no grade for the item, skip it
            if  not note.strip():
                continue
            
            lp = item[4]
            logger.info(f"[{bezeichnung}] {(max_len - len(bezeichnung)) * ' '} note=[{note}]{(8 - len(note)) * ' '} lp=[{lp}]")
            all_grades.append(note)
            all_points.append(lp)
    
    try:
        numeric_grades = [float(grade.replace(',', '.')) for grade in all_grades if grade.replace(',', '.').replace('.', '', 1).isdigit()]
        average_grade = sum(numeric_grades) / len(numeric_grades) if numeric_grades else 0.0
    except Exception as e:
        logger.exception(f"Error calculating average grade: {e}")
        average_grade = 0.0
    
    try:
        total_points = sum(float(lp.replace(',', '.')) for lp in all_points if lp.replace(',', '.').replace('.', '', 1).isdigit())
    except Exception as e:
        logger.exception(f"Error calculating total points: {e}")
        total_points = 0.0
    logger.info(f"Average Grade: {average_grade:.2f}, Total Points: {total_points:.2f}")

if __name__ == "__main__":
    logger, LOG_FILENAME = setup_logging()

    driver = init_driver(headless=True)

    username = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')
    login_url = "https://lsf.uni-hildesheim.de/"

    ok = login(driver, login_url, username, password)
    if ok is False:
        logger.error("Login aborted due to missing credentials or login error. Exiting.")
        driver.quit()
        raise SystemExit(1)

    time.sleep(1.5)
    logger.info("Waiting briefly after login...")

    data = fetch_table_data(driver, pattern="Notenspiegel")
    process_and_log_data(data, logger)

    logger.info(f"Logs written to: {LOG_FILENAME}")
    driver.quit()
