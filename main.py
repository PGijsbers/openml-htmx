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
        endpoint=f"http://localhost:8000/datasets/{dataset['did']}",
        ) for dataset in (datasets if forward else reversed(datasets))
    ]
    new_offset = offset + limit if forward else offset - limit

    # This infinite scroll loads nicely and typically in time as it is presented before
    # the latest results. However, on very fast scrolling, the revealed trigger may be
    # missed. In that case no further results are loaded, unless you scroll back up
    # to get a revealed trigger. This is something I can live with for now, but may
    # be circumvented by placing a back-up reveal trigger at the bottom. There should
    # be caution to remove that trigger on a successful load of the leading trigger.

    next_ = '''<div
            hx-get="$endpoint"
            hx-trigger="revealed"
            hx-swap="afterend"
            hx-target=".dataset-list div:last-child"
            title="Loading $endpoint">loader</div>'''.replace(
        "$endpoint",f"http://localhost:8000/datasets/offset/{new_offset}/limit/{limit}"
    )
    return ''.join([next_] + items)

@app.get("/datasets/{id_}", response_class=HTMLResponse)
def dataset_card(id_: int):
    dataset = get_dataset(id_)
    dataset["description"] = markdown.markdown(dataset["description"])

    with open("html/dataset-card.html", "r") as fh:
        template = Template(fh.read())
    return template.substitute(
        **dataset,
        openml_url=f"https://openml.org/d/{id_}",
    )
