import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

handler = logging.StreamHandler()
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


TIMEOUT: int = 1000000


def main(driver, **kwargs) -> str:
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
    from lambda_function import get_driver
    print(main(get_driver(), query="dog"))
