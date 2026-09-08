UMB Observatory
=================

This project manages a joint docker file with selected versions of different PMC tools and libraries,
a jupyter server, and a collection of python files that help to ensure that are mutually compatible. 


The container
-------------
Is created from the docker file, released to github daily via CI. 
On the container, you find 
- a version of storm (with UMB support),
- a version of prism (with UMB support),
- the umbi python library.
- the contents of this repo, in particular, the umbtest library.
- A jupyter notebook that is running. 

The Dockerfile builds prism from source (the `umb` branch of
`davexparker/prism`, overridable via the `prism_repo`/`prism_branch` build
arguments) and downloads Modest. Storm is not built from source: the image
is based on the official prebuilt `movesrwth/storm:ci` container (a daily
snapshot of Storm `master`, with UMB support), which saves a long Storm
compilation. The base image can be overridden via the `BASE_IMAGE` build
argument. 

### Running the docker

You can build the docker container yourself or obtain it by:

```
docker pull ghcr.io/pmc-tools/umb-observatory:main
```

Then, to start it, we recommend:
```
docker run --name pmcdocker -d -p 8000:8000 ghcr.io/pmc-tools/umb-observatory:main
```

The exposed port helps you connect to the notebooks. If port 8000 is already occupied locally,
you can change it to `-p 8001:8000`, or something like that. 

### Connecting to the notebook

First, run 
```
docker exec pmcdocker jupyter server list
```
The link in there will typically not work. However, you can find a token as part of the listed url. 
Copy this token. 

You can connect to `localhost:8000` (or another port, if you changed it) in your browser.
The notebook will ask for a token. Paste the token you just copied. 
You are now in a jupyter notebook. 

You can go to `getting_started.ipynb` (in the docker container) to get started
with some opportunities that UMB offers.

The notebook is written in markdown (`getting_started.md`, the tracked source of
truth) and materialized as `.ipynb` when the container image is built. Locally,
regenerate the notebook with:
```
jupytext --to ipynb getting_started.md
```
JupyterLab users can install the jupytext extension to open the `.md` directly.


Umbtest
-------

Umbtest is a set python files that check that UMB support is aligned. 
The best place to get started is probably in `tests/test_toolchains.py`.
Roughly `umbtest/benchmarks.py` collects files we use for testing,
while `umbtest/tools.py` provides a thin layer around the available tools. 

You can use umbtest in different ways. 
The preferred way is via the docker, which ensures that you have the right tools installed in known locations. 

### Via the docker
This is possible in two ways: via a notebook and via the command line. 

#### Via the notebook
As explained in the notebook, to which you can connect as explained above. 

#### From the command line
In particular, you can run: 
```
docker exec pmcdocker python -m pytest 
```
By default the tests run on the small quick benchmark suite (10 models) in
`umbtest.benchmarks.quick_prism_files`. To verify UMB support end-to-end across
all models, run the full suite:
```
docker exec pmcdocker env UMB_TEST_MODELS=full python -m pytest
```
The CI workflow runs the full suite.

### Locally
UMBTest is currently not available as a standalone package.
However, you can run the scripts directly on your local machine.

1. Configure the tool paths. Copy `tools.toml.example` to `tools.toml` and fill in
   your local installation paths (or set the `UMB_STORM`, `UMB_PRISM`, `UMB_MODEST`
   environment variables). `tools.toml` is not tracked by git.
2. `pip install umbi`
3. - You can run `python -m pytest tests` to run all kind of tests
   - Run `python main.py` for a simple script
   - Or run the python notebook on your local jupyterserver (see above for details)
   - Run `ruff check umbtest tests main.py` and `pyright` for static checks

Continuous Integration
-----------------------
This repo is hosted on github, where continuous integration runs Umbtests:
https://github.com/pmc-tools/umb-observatory/actions/workflows/test.yml

