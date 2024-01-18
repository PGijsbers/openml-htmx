from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from openml import get_datasets

app = FastAPI()


@app.get("/blue", response_class=HTMLResponse)
def get_blue():
    dataset = get_datasets()[-1]["name"]
    return f"<div style=\"background:blue;color:white;\">{dataset}</div>"

@app.get("/", response_class=HTMLResponse)
def get_home():
    with open("index.html", "r") as f:
        return f.read()
