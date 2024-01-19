import httpx

OPENML_URL = "https://test.openml.org/py"

def get_datasets():
    response = httpx.post(
        f"{OPENML_URL}/datasets/list",
        json={"pagination": {"offset": 10, "limit": 5}}
    )
    return response.json()

def get_dataset(id_: int):
    r = httpx.get(
        f"{OPENML_URL}/datasets/{id_}"
    )
    return r.json()
