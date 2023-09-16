import csv
import json
import random

import boto3

NUM_PROXIES = 10


def get_lambda_function():
    round_robin = 0
    while True:
        yield "selenium-" + str(round_robin)
        round_robin = (round_robin + 1) % NUM_PROXIES


if __name__ == "__main__":
    lambda_client = boto3.client("lambda")
    lambda_function = get_lambda_function()

    with open("dogs.txt", mode="r") as file:
        csv_reader = csv.reader(file)
        dogs = [row[0] for row in csv_reader]

    while True:
        dog = random.choice(dogs)
        response = json.loads(
            lambda_client.invoke(
                FunctionName=next(lambda_function),
                InvocationType="RequestResponse",
                Payload=json.dumps({"src": open("example.py").read(), "query": dog}),
            )["Payload"].read()
        )

        if "body" not in response:
            raise Exception(response)

        print(dog)
        print(response["body"])
        print()
