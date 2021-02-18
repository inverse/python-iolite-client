# Python IOLite Client

![CI](https://github.com/inverse/python-iolite-client/workflows/CI/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a38c5dbfc12247c893b4f39db4fac2b2)](https://www.codacy.com/manual/inverse/python-iolite-client?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=inverse/python-iolite-client&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/a38c5dbfc12247c893b4f39db4fac2b2)](https://www.codacy.com/manual/inverse/python-iolite-client?utm_source=github.com&utm_medium=referral&utm_content=inverse/python-iolite-client&utm_campaign=Badge_Coverage)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

WIP Python client for [IOLite's][0] remote API.

Build by reverse engineering the [Deutsche Wohnen][2] [MIA Android App][1]. I wrote a [short post][3] on how I achieved
that.

The client is still incomplete, but the authentication layer, some basic command models and a client to change the
heating intervals are available.

## Requirements

-   Python 3.6+
-   [Pipenv][4]

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

You can decode the base64 encoded basicAuth information using the `scripts/get_credentials.py` script (see [development](#development) section).

## Development

-   Init your pipenv environment (`pipenv install`)
-   Copy `.env.example` to `.env`
-   Decode credentials (`pipenv run python scripts/get_credentials.py <basic-auth-value>`)
-   Add your credentials to `.env` following the above process

The [pre-commit][5] framework is used enforce some linting and style compliance on CI.

To get the same behaviour locally you can run `pre-commit install` within your activated venv.

Alternatively to run manually you can run `pre-commit run -a`.

## Access remote UI

Run `pipenv run python scripts/example.py` and copy the URL to your browser of choice.

You will need the HTTP basic credentials you defined earlier within the `.env` file.

## Usage example

A jupyter notebook showcasing the heating interval scheduler can be found in `notebooks/Heating Scheduler.ipynb`. To
access the notebook run the `pipenv run jupyter notebook` command.

## Licence

MIT

[0]: https://iolite.de/

[1]: https://play.google.com/store/apps/details?id=de.iolite.client.android.mia

[2]: https://deutsche-wohnen.com/

[3]: https://www.malachisoord.com/2020/08/06/reverse-engineering-iolite-remote-api/

[4]: https://pipenv.pypa.io/en/latest/#install-pipenv-today

[5]: https://pre-commit.com/
