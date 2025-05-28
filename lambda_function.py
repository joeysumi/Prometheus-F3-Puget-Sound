import json
import os

from prometheus import Prometheus


def lambda_handler(event, context):
    creds = {
        "host": os.environ.get("host"),
        "database": os.environ.get("database"),
        "username": os.environ.get("username"),
        "password": os.environ.get("password"),
    }
    app = Prometheus(credentials=creds)
    app.run()
    return {
        "statusCode": 200,
        "body": json.dumps("Prometheus Run")
    }


if __name__ == "__main__":
    lambda_handler('a', 'b')
