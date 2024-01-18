import httpx

OPENML_URL = "https://test.openml.org/py"

def get_datasets():
    r = httpx.post(
        f"{OPENML_URL}/datasets/list",
        json={"pagination": {"offset": 10, "limit": 5}}
    )
    return r.json()
