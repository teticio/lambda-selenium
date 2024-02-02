import asyncio
import csv
import json
import logging

import aioboto3
from tqdm import tqdm

handler = logging.StreamHandler()
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

NUM_PROXIES = 10
MAX_REQUESTS_PER_PROXY = 50


def get_lambda_function():
    round_robin = 0
    while True:
        yield "selenium-" + str(round_robin)
        round_robin = (round_robin + 1) % NUM_PROXIES


async def process_chunk(client, chunk, function_name, src):
    results = list()
    for item in tqdm(chunk, desc=function_name):
        try:
            response = json.loads(
                await (
                    await client.invoke(
                        FunctionName=function_name,
                        InvocationType="RequestResponse",
                        Payload=json.dumps({"src": src, "query": item}),
                    )
                )["Payload"].read()
            )
            if "body" not in response:
                raise Exception(response)
            results.append(response["body"])

        except Exception as e:
            logger.error(e)
            results.append(e)

    return results


async def main():
    async with aioboto3.Session().client("lambda") as client:
        lambda_function = get_lambda_function()

        with open("dogs.txt", mode="r") as file:
            csv_reader = csv.reader(file)
            items = [row[0] for row in csv_reader]

        chunk_size = min(
            max(1, len(items) // (NUM_PROXIES - 1)), MAX_REQUESTS_PER_PROXY
        )
        chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

        src = open("example.py").read()
        tasks = [
            process_chunk(client, chunk, next(lambda_function), src) for chunk in chunks
        ]
        for chunk, results in zip(chunks, await asyncio.gather(*tasks)):
            for query, result in zip(chunk, results):
                logger.info(query)
                logger.info(result)
                logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
