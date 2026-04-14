from pathlib import Path

import requests


def run() -> None:
    data_dir = Path(__file__).parent.parent.joinpath("data")
    response = requests.post("http://localhost:8000/upload", files={"file": open(data_dir.joinpath("2026-ev9.pdf"), "rb")})
    print(response.json())

    response = requests.post("http://localhost:8000/upload", files={"file": open(data_dir.joinpath("test.txt"), "rb")})
    print(response.json())

if __name__ == "__main__":
    run()