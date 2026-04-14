from pathlib import Path

import requests


def run() -> None:
    response = requests.get("http://localhost:8000/status")
    print(response.json())

if __name__ == "__main__":
    run()