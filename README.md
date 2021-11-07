# Python IOLite Client

![CI](https://github.com/inverse/python-iolite-client/workflows/CI/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a38c5dbfc12247c893b4f39db4fac2b2)](https://www.codacy.com/manual/inverse/python-iolite-client?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=inverse/python-iolite-client&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/inverse/python-iolite-client/branch/master/graph/badge.svg?token=26LC98A22C)](https://codecov.io/gh/inverse/python-iolite-client)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

WIP Python client for [IOLite's][0] remote API.

The client is still incomplete, but the authentication layer, some basic command models, and a client to change the
heating intervals are available.

Build by reverse engineering the [Deutsche Wohnen][2] [MIA Android App][1] and subsequently their remote API.

Read the following [short post][3] on how that was achieved.

## Requirements

-   Python 3.7+
-   [Poetry][4]

## Getting credentials

Open your Deutsche Wohnen tablet and begin pairing device process. Scan the QR code with your QR-Scanner and instead of
opening the QR code in your browser, copy it's content. You'll get the following payload:

```json
{
  "webApp": "/ui/",
  "code": "<redacted>",
  "basicAuth": "<redacted>"
}
```

-   `basicAuth` contains base64 encoded HTTP basic username and password. Decode this to get the `:` separated `user:pass`.
-   `code` is the pairing code

You can decode the credentials using the `scripts/get_credentials.py` script. e.g.

```bash
 python scripts/get_credentials.py '{"webApp":"/ui/","code":"<redacted>","basicAuth":"<redacted>"}'
```

## Development

-   Init your virtualenv environment (`poetry install`)
-   Copy `.env.example` to `.env`
-   Decode credentials (`poetry run python scripts/get_credentials.py <basic-auth-value>`)
-   Add your credentials to `.env` following the above process

The [pre-commit][5] framework is used enforce some linting and style compliance on CI.

To get the same behaviour locally you can run `pre-commit install` within your activated venv.

Alternatively to run manually you can run `pre-commit run -a`.

## Access remote UI

Run `poetry run python scripts/example.py` and copy the URL to your browser of choice.

You will need the HTTP basic credentials you defined earlier within the `.env` file.

Be sure to run `poetry install -E dev` to get the required dependencies for this.

## Usage example

A jupyter notebook showcasing the heating interval scheduler can be found in `notebooks/Heating Scheduler.ipynb`. To
access the notebook install [jupyter notebook or jupyter lab](https://jupyter.org/install.html) into the virtual environment and run the notebook:

```sh
poetry shell
pip install notebook
jupyter notebook
```

If running the notebook gives you a `ModuleNotFoundError`, you may fix this issue by changing the notebook's kernel (following [this StackOverflow post](https://stackoverflow.com/a/47296960/50913)):

```sh
poetry shell
python -m ipykernel install --user --name=`basename $VIRTUAL_ENV`
```

Then switch the kernel in the notebook's top menu under: _Kernel > Change Kernel_.

## Licence

MIT

[0]: https://iolite.de/

[1]: https://play.google.com/store/apps/details?id=de.iolite.client.android.mia

[2]: https://deutsche-wohnen.com/

[3]: https://www.malachisoord.com/2020/08/06/reverse-engineering-iolite-remote-api/

[4]: https://python-poetry.org/

[5]: https://pre-commit.com/
