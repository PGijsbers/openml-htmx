# OpenML Dataset Browser
I wanted to explore the [HTMX](https://htmx.org) framework and the [HATEOAS](https://htmx.org/essays/hateoas/) concept, so I decided to make this page to browse OpenML datasets.
This project is essentially a middle-man: it connects to an OpenML API to fetch data from OpenML, and can then serve HTML components to the client.

## Installation
Just install the dependencies in a new virtual environment:
```commandline
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```
You can then run the server with `uvicorn`, when developing it is useful to have automatic reloads enabled:
```
uvicorn main:app --reload
```
