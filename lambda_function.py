import importlib.util
import logging
import unittest.mock as mock
from tempfile import NamedTemporaryFile, gettempdir

with mock.patch("multiprocessing.Lock", return_value=object()):
    import undetected_chromedriver as uc

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_driver() -> uc.Chrome:
    tempdir = gettempdir()
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
    return uc.Chrome(options=options)


def lambda_handler(event, context):  # pylint: disable=unused-argument
    src = event.pop("src")

    if not src:
        return {"statusCode": 400, "body": "Missing src parameter"}

    with NamedTemporaryFile(mode="w", suffix=".py") as temp:
        temp.write(src)
        temp.flush()

        spec = importlib.util.spec_from_file_location("module.name", temp.name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "main"):
            return {
                "statusCode": 400,
                "body": "Missing main function",
            }

        result = module.main(get_driver(), **event)

    return {"statusCode": 200, "body": str(result)}
