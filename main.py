import markdown
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from string import Template

from openml import get_datasets, get_dataset

app = FastAPI()


@app.get("/blue", response_class=HTMLResponse)
def get_blue():
    with open("html/dataset-card.html", "r") as fh:
        template = Template(fh.read())
    last_id = get_datasets()[-1]["did"]
    dataset = get_dataset(last_id)
    openml_url = f"https://openml.org/d/{last_id}"
    dataset["description"] = markdown.markdown(dataset["description"])
    return template.substitute(**dataset, openml_url=openml_url)

@app.get("/", response_class=HTMLResponse)
def get_home():
    with open("index.html", "r") as f:
        return f.read()
