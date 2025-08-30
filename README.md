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

You can build the docker container yourself or obtain it from 

### Connecting to the notebook



Umbtest
--------