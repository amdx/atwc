# Python TWC

Python interface to NoMagic/CATIA Teamwork Cloud Server.

[Teamwork Cloud](https://www.3ds.com/products-services/catia/products/no-magic/teamwork-cloud/) server is a central
repository service to store and retrieve [Cameo](https://www.3ds.com/products-services/catia/products/no-magic/cameo-systems-modeler/)
and [MagicDraw](https://www.3ds.com/products-services/catia/products/no-magic/magicdraw/) models.

TWC exposes a REST API that allows interaction with the stored models.

This library has been primarily written as interface abstraction for
Archimedes Exhibitions GmbH's Cameo Collaborator Publisher service, hence it's
not intended as a general-purpose solution.

## Running the examples

Copy the file `config.py.dist` into `config.py` in the `examples` folder:

```bash
$ cd examples
$ cp config.py.dist config.py
```

Edit the file `config.py` and replace the placeholders for all the entries.

More information can be found in the docstring of each script.
