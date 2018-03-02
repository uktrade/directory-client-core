# directory-client-core

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![gemnasium-image]][gemnasium]

**Directory Client Core.**

Common code for the Directory API clients.
---

## Requirements

## Installation

```shell
pip install -e git+https://git@github.com/uktrade/directory-client-core.git@0.0.1#egg=directory-client-core
```

## Usage

```python
from directory_client_core.client import ClientBase


class MyAPIClient(ClientBase):
    def get_something(self):
        return self.get(...)

    def create_sometime(self):
        return self.post(...)
```

## Development

    $ git clone https://github.com/uktrade/directory-client-core
    $ cd directory-ui
    $ make

[code-climate-image]: https://codeclimate.com/github/uktrade/directory-client-core/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-client-core

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-client-core/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-client-core/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-client-core/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-client-core

[gemnasium-image]: https://gemnasium.com/badges/github.com/uktrade/directory-client-core.svg
[gemnasium]: https://gemnasium.com/github.com/uktrade/directory-client-core
