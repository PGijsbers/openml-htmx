import markdown
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from string import Template

from openml import get_datasets, get_dataset

app = FastAPI()



@app.get("/", response_class=HTMLResponse)
def get_home():
    with open("index.html", "r") as f:
        return f.read()


@app.get("/datasets/last/{number}", response_class=HTMLResponse)
def get_last_datasets(number: int):
    # There no other way to figure out the offset for the listing
    offset = 6000
    limit = 100
    while (datasets := get_datasets(offset, limit)) and isinstance(datasets, dict):
        offset -= limit
        assert offset >= 0

    offset = offset + len(datasets) - 20
    return get_dataset_items(offset, 20)

@app.get("/datasets/offset/{offset}/limit/{limit}", response_class=HTMLResponse)
def get_dataset_items(offset: int, limit: int, forward: bool = False):
    datasets = get_datasets(offset, limit)
    for dataset in datasets:
        dataset["quality"] = dict(
            tuple(q.values())
            for q in dataset["quality"]
        )

    with open("html/dataset-list-item.html", "r") as fh:
        template = Template(fh.read())

    items = [template.substitute(
        id=dataset["did"],
        name=dataset["name"],
        rows=dataset["quality"].get("NumberOfInstances", "?"),
        features=dataset["quality"].get("NumberOfFeatures", "?"),
        classes=dataset["quality"].get("NumberOfClasses", "?"),
        ) for dataset in (datasets if forward else reversed(datasets))
    ]
    new_offset = offset + limit if forward else offset - limit
    with open("html/replace-on-reveal.html", "r") as fh:
        ror_template = Template(fh.read())
    next_ = ror_template.substitute(endpoint=f"http://localhost:8000/datasets/offset/{new_offset}/limit/{limit}")
    return ''.join(items + [next_])
