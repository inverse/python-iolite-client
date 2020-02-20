# Python IOLite Client

![CI](https://github.com/inverse/python-iolite-client/workflows/CI/badge.svg)

WIP Python client for [IOLite's][0] remote API.

Build by reverse engineering the [Deutsche Wohnen][2] [MIA Android App][1].

# Requirements

- Python 3.8
- Pipenv

# Getting credentials

Open your Deutsche Wohnen tablet and begin pairing device process. Scan QR code and you'll get the following payload.

```json
{"webApp":"/ui/","code":"<redacted>","basicAuth":"<redacted>"}
```

- `basicAuth` contains base64 encoded HTTP basic username and password.
- `code` is the pairing code

# Playground

- Copy `.env.example` to `.env`
- Add your credentials to `.env` following the above process
- init your pipenv environment
- Run `example.py`

Once you've generated the `SID` you can use it in conjunction with the HTTP basic authentication credentials to access 
the remote UI on your browser of choice.

```
https://remote.iolite.de/ui/?SID=<SID>
```

# Licence

MIT

[0]: https://iolite.de/
[1]: https://play.google.com/store/apps/details?id=de.iolite.client.android.mia
[2]: https://deutsche-wohnen.com/