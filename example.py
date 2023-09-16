import logging
import tempfile
import unittest.mock as mock

with mock.patch("multiprocessing.Lock", return_value=object()):
    import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

handler = logging.StreamHandler()
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


TIMEOUT: int = 1000000

tempdir = tempfile.gettempdir()
options: uc.ChromeOptions = uc.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--hide-scrollbars")
options.add_argument("--single-process")
options.add_argument("--ignore-certificate-errors")
options.add_argument(f"--homedir={tempdir}")
options.add_argument(f"--disk-cache-dir={tempdir}/cache-dir")
options.add_argument(f"--data-path={tempdir}/data-path")
options.add_experimental_option("prefs", {"download.default_directory": tempdir})
logger.debug("Opening driver")
driver: uc.Chrome = uc.Chrome(options=options)


def main(**kwargs):
    query: str = kwargs.pop("query")

    logger.debug("Navigating to Google")
    driver.get("https://www.google.com/?q=" + query)

    logger.debug("Waiting for Accept All button")
    WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//div[text()='Accept all']]"))
    ).click()

    logger.debug("Waiting for Google Search button")
    driver.execute_script(
        "arguments[0].click();",
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@value='Google Search']")
            )
        ),
    )

    logger.debug("Waiting for results")
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='result-stats']"))
    )

    results = driver.find_elements(By.XPATH, "//div[@class='kno-rdesc']")
    return results[0].text if len(results) > 0 else ""


if __name__ == "__main__":
    print(main(query="dog"))
