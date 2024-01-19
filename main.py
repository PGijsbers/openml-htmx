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

@app.get("/datasets/offset/{offset}/limit/{limit}", response_class=HTMLResponse)
def get_dataset_items(offset: int, limit: int, forward: bool = True):
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
        ) for dataset in datasets
    ]
    new_offset = offset + limit if forward else offset - limit
    with open("html/replace-on-reveal.html", "r") as fh:
        ror_template = Template(fh.read())
    next_ = ror_template.substitute(endpoint=f"http://localhost:8000/datasets/offset/{new_offset}/limit/{limit}")
    return ''.join(items + [next_])
