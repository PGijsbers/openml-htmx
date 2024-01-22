import markdown
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from string import Template

from openml import get_datasets, get_dataset

SUFFIX = "/htmx"
HOST = "http://test.openml.org"
HTMX_URL = f"{HOST}{SUFFIX}"

app = FastAPI(root_path=SUFFIX)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def get_home():
    with open("index.html", "r") as f:
        return Template(
		f.read()
	).substitute(HTMX_URL=HTMX_URL, stylesheet=f"{HTMX_URL}{SUFFIX}/static/style.css")


@app.get("/datasets/last/{number}", response_class=HTMLResponse)
def get_last_datasets(number: int):
    # There no other way to figure out the offset for the listing
    return get_dataset_items(0, 20, forward=True)
    offset = 6000
    limit = 100
    while (datasets := get_datasets(offset, limit)) and isinstance(datasets, dict):
        offset -= limit
        assert offset >= 0

    offset = offset + len(datasets) - 20
    offset=0
    return get_dataset_items(offset, 20, forward=True)

def round_to_suffix(number: int) -> str:
    if number < 1000:
        return f"{number:.3g}"
    if number < 1_000_000:
        return f"{number / 1_000:.3g}K"
    if number < 1_000_000_000:
        return f"{number / 1_000_000:.3g}M"
    return f"{number / 1_000_000_000:.3g}B"

@app.get("/datasets/offset/{offset}/limit/{limit}", response_class=HTMLResponse)
def get_dataset_items(offset: int, limit: int, forward: bool = True):
    datasets = get_datasets(offset, limit)
    for dataset in datasets:
        dataset["quality"] = dict(
            tuple(q.values())
            for q in dataset["quality"]
        )

        task_type = dataset["quality"].get("NumberOfClasses", "?")
        dataset["task_type"] = {0: "regression", 2: "binary classification", "?": "No default target"}.get(
            task_type, "multi-class classification"
        )
        if isinstance(rows := dataset["quality"].get("NumberOfInstances", "?"), (int, float)):
            rows = round_to_suffix(rows)
        dataset["rows"] = rows

        if isinstance(features := dataset["quality"].get("NumberOfFeatures", "?"), (int, float)):
            features = round_to_suffix(features)
        dataset["features"] = features
    with open("html/dataset-list-item.html", "r") as fh:
        template = Template(fh.read())

    items = [template.substitute(
        id=dataset["did"],
        name=dataset["name"],
        rows=dataset["rows"],
        features=dataset["features"],
        classes=dataset["task_type"],
        endpoint=f"{HTMX_URL}/datasets/{dataset['did']}",
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
            hx-target=".dataset-list > div:last-child"
            title="Loading $endpoint"></div>'''.replace(
        "$endpoint",f"{HTMX_URL}/datasets/offset/{new_offset}/limit/{limit}"
    )
    return ''.join([next_] + items)

@app.get("/datasets/{id_}", response_class=HTMLResponse)
def dataset_card(id_: int):
    dataset = get_dataset(id_)
    if dataset["description"] == "":
        dataset["description"] = "No description provided."
    dataset["description"] = markdown.markdown(dataset["description"])

    with open("html/dataset-card.html", "r") as fh:
        template = Template(fh.read())
    return template.substitute(
        **dataset,
        openml_url=f"https://openml.org/d/{id_}",
    )


