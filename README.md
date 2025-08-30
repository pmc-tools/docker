PMC Tools Docker
=================

This project manages a joint docker file with selected versions of different PMC tools.
The project furthermore manages some joint python files that help to ensure that common file formats are mutually compatible. 

The container
-------------
Is created from the docker file, released to github daily via CI. 
On the container, you find 
- a version of storm (with UMB support),
- a version of prism (with UMB support),
- the umbi python library
- the contents of this repo, in particular, the umbtest library.
- A jupyter notebook that is running. 

### Running the docker

You can build the docker container yourself or obtain it by:

```
docker pull ghcr.io/pmc-tools/docker:main
```

Then, to start it, we recommend:
```
docker run --name pmcdocker -d -p 8000:8000 ghcr.io/pmc-tools/docker:main 
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

You can go to getting_started.ipynb to get started with what this docker container has to offer.
(TO BE DONE.)

Umbtest
-------
You can interact with Umbtest in different ways. 
The easiest


Continuous Integration
-----------------------
This repo is hosted on github, where continuous integration runs Umbtests.