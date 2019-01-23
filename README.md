# directory-client-core

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![pypi-image]][pypi]

**Directory Client Core.**

Common code for the Directory API clients.
---

## Requirements

## Installation

```shell
pip install directory-client-core
```

## Usage

```python
from directory_client_core.base import AbstractAPIClient


class MyAPIClient(AbstractAPIClient):

    version = 1  # passed as a header in all requests

    def get_something(self):
        return self.get(...)

    def create_sometime(self):
        return self.post(...)


client = MyAPIClient(
    base_url='https://example.com/',
    api_key='test',
    sender_id='test-sender-id',
    timeout=2,
)

response = client.get_something()
```

### Caching

The decorator `directory_client_core.helpers.fallback` can be used to cache the responses from the remote server, allowing the cached content to be later used if the remote server does not return the up to date live content (maybe it times out, maybe the server is down). This decorator also saves etag response headers to later expose them in requests and respect 304 (Not modified) response and serve already cached contents.

```
# settings.py
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 days

# client.py

from django.core.cache import caches

from directory_client_core import helpers
from directory_client_core.base import AbstractAPIClient


class APIClient(AbstractAPIClient):
    version = 1

    @helpers.fallback(cache=caches['fallback'])
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def retrieve(self):
        return self.get(url='/some/path/')
```

## Development

    $ git clone https://github.com/uktrade/directory-client-core
    $ cd directory-client-core

## Publish to PyPI

The package should be published to PyPI on merge to master. If you need to do it locally then get the credentials from rattic and add the environment variables to your host machine:

| Setting                     |
| --------------------------- |
| DIRECTORY_PYPI_USERNAME     |
| DIRECTORY_PYPI_PASSWORD     |


Then run the following command:

    make publish


[code-climate-image]: https://codeclimate.com/github/uktrade/directory-client-core/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-client-core

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-client-core/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-client-core/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-client-core/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-client-core

[pypi-image]: https://badge.fury.io/py/directory-client-core.svg
[pypi]: https://badge.fury.io/py/directory-client-core
