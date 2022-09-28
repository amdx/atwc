# aTWC - Python interface to Teamwork Cloud

Python interface to NoMagic/CATIA Teamwork Cloud Server.

[Teamwork Cloud](https://www.3ds.com/products-services/catia/products/no-magic/teamwork-cloud/) server is a central
repository service to store and retrieve [Cameo](https://www.3ds.com/products-services/catia/products/no-magic/cameo-systems-modeler/)
and [MagicDraw](https://www.3ds.com/products-services/catia/products/no-magic/magicdraw/) models.

TWC exposes a REST API that allows interaction with the stored models.

This library has been primarily written as interface abstraction for
Archimedes Exhibitions GmbH's Cameo Collaborator Publisher service, hence it's
not intended as a general-purpose solution.

aTWC is developed and maintained by [Archimedes Exhibitions GmbH](https://www.archimedes-exhibitions.de). 

## Installation

```bash
$ pip3 install atwc
```

## Usage example

```python
import asyncio
import atwc


async def main():
    client = atwc.client.Client('https://twc.local:8111/osmc/', 'user', 'password')

    async with client.create_session():
        browser = atwc.browsers.ResourceBrowser(client)
        await browser.fetch()

        print('MagicDraw resources:')
        for resource in browser.md_resources:
            print(f'  {await browser.get_category_path(resource)}/'
                  f'{resource["dcterms:title"]}')


asyncio.run(main())
```

## Running the examples

Copy the file `config.py.dist` into `config.py` in the `examples` folder:

```bash
$ cd examples
$ cp config.py.dist config.py
```

Edit the file `config.py` and replace the placeholders for all the entries.

More information can be found in the docstring of each script.
