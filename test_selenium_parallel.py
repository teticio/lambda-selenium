import concurrent.futures
import csv
import json
import logging

import boto3
from botocore.client import Config
from tqdm import tqdm

handler = logging.StreamHandler()
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

NUM_PROXIES = 10
MAX_REQUESTS_PER_PROXY = 20


def get_lambda_function():
    round_robin = 0
    while True:
        yield "selenium-" + str(round_robin)
        round_robin = (round_robin + 1) % NUM_PROXIES


def process_chunk(chunk, function_name, src):
    config = Config(max_pool_connections=NUM_PROXIES)
    client = boto3.client("lambda", config=config)

    results = list()
    for item in tqdm(chunk):
        try:
            response = json.loads(
                client.invoke(
                    FunctionName=function_name,
                    InvocationType="RequestResponse",
                    Payload=json.dumps({"src": src, "query": item}),
                )["Payload"].read()
            )
            if "body" not in response:
                raise Exception(response)
            results.append(response["body"])

        except Exception as e:
            logger.error(e)
            results.append(e)

    return results


if __name__ == "__main__":
    client = boto3.client("lambda")
    lambda_function = get_lambda_function()

    with open("dogs.txt", mode="r") as file:
        csv_reader = csv.reader(file)
        items = [row[0] for row in csv_reader]

    chunk_size = min(max(1, len(items) // (NUM_PROXIES - 1)), MAX_REQUESTS_PER_PROXY)
    chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

    src = open("example.py").read()
    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_PROXIES) as executor:
        futures = {
            executor.submit(
                process_chunk,
                chunk=chunk,
                function_name=next(lambda_function),
                src=src,
            ): chunk
            for chunk in chunks
        }

        for future in concurrent.futures.as_completed(futures):
            for query, result in zip(futures[future], future.result()):
                logger.info(query)
                logger.info(result)
                logger.info("=" * 80)
