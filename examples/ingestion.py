from pathlib import Path

import requests


def run() -> None:
    data_dir = Path(__file__).parent.parent.joinpath("data")
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": open(data_dir.joinpath("2026-ev9.pdf"), "rb")},
        timeout=10,
    )
    print(response.json())

    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": open(data_dir.joinpath("test.txt"), "rb")},
        timeout=10,
    )
    print(response.json())

    response = requests.get("http://localhost:8000/files", timeout=10)
    print(response.json())

    response = requests.delete("http://localhost:8000/files/2026-ev9.pdf", timeout=10)
    print(response.json())

    response = requests.get("http://localhost:8000/files", timeout=10)
    print(response.json())

if __name__ == "__main__":
    run()