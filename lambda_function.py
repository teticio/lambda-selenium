import importlib.util


def lambda_handler(event, context):  # pylint: disable=unused-argument
    python_code = event.pop("src")

    if not python_code:
        return {"statusCode": 400, "body": "Missing src parameter"}

    file_name = "/tmp/src.py"
    with open(file_name, "w") as f:
        f.write(python_code)

    spec = importlib.util.spec_from_file_location("module.name", file_name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "main"):
        return {
            "statusCode": 400,
            "body": "Missing main function.",
        }

    return {"statusCode": 200, "body": str(module.main(**event))}
