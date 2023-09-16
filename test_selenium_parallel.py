import csv
import json
import random
from concurrent.futures import ThreadPoolExecutor

import boto3

NUM_PROXIES = 10


def get_lambda_function():
    round_robin = 0
    while True:
        yield "selenium-" + str(round_robin)
        round_robin = (round_robin + 1) % NUM_PROXIES


def invoke_lambda(dog, function_name, client, payload_src):
    response = json.loads(
        client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({"src": payload_src, "query": dog}),
        )["Payload"].read()
    )

    if "body" not in response:
        raise Exception(response)

    print(dog)
    print(response["body"])
    print()


if __name__ == "__main__":
    lambda_client = boto3.client("lambda")
    lambda_function = get_lambda_function()

    with open("dogs.txt", mode="r") as file:
        csv_reader = csv.reader(file)
        dogs = [row[0] for row in csv_reader]
    random.shuffle(dogs)

    chunk_size = len(dogs) // NUM_PROXIES
    chunks = [dogs[i : i + chunk_size] for i in range(0, len(dogs), chunk_size)]
    if len(dogs) % NUM_PROXIES:
        chunks[-1].extend(dogs[-(len(dogs) % NUM_PROXIES) :])

    for chunk in chunks:
        with ThreadPoolExecutor() as executor:
            function_name = next(lambda_function)
            payload_src = open("example.py").read()
            executor.map(
                lambda dog: invoke_lambda(
                    dog, function_name, lambda_client, payload_src
                ),
                chunk,
            )
