import httpx

OPENML_URL = "https://test.openml.org/py"

def get_datasets(offset: int, limit: int):
    response = httpx.post(
        f"{OPENML_URL}/datasets/list",
        json={"pagination": {"offset": offset, "limit": limit},
              "apikey": "00000000000000000000000000000000",
              "status": "active"}
    )
    return response.json()

def get_dataset(id_: int):
    r = httpx.get(
        f"{OPENML_URL}/datasets/{id_}"
    )
    return r.json()
