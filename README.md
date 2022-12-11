# Lumiere Client for Lifx lights (Python)

A python implementation for [Lumiere](https://github.com/lumiere-lighting) (community-controlled lighting) integration with [Lifx](https://www.lifx.com/) lights.

## Install

1. Get code.
2. Install dependencies: `pip install -r requirements.txt`

## Configure

Utilize environment variables to configure.  Optionally put in a `.env` file.

- `LUMIERE_API_DOMAIN`: URL of [Lumiere API server](https://github.com/lumiere-lighting/lumiere-api) to connect websocket to.  Defaults to `https://api.lumiere.lighting`.
- `LUMIERE_LIFX_API_KEY`: [Lifx API key](https://cloud.lifx.com/settings) to use.
- `LUMIERE_LIFX_LIGHTS`: [Lifx light selector](https://api.developer.lifx.com/reference/selectors) to update specific lights; defaults to `all`.
- `LUMIERE_LIFX_BRIGHTNESS`: Brightness to set with lights; should be between 0 and 1; defaults to `0.85`.
- `LUMIERE_LIFX_DURATION`: Seconds on light transition time; defaults to `1`.
- `LOG_LEVEL`: Python [logging level](https://docs.python.org/3/library/logging.html#levels); defaults to `30`.

## Usage

Run with:

```bash
python lumiere-client-lifx/client.py
```

## Deploy

### Linux init.d service

Install dependencies.

- (see above)

Install the startup/service script.

- Copy the `init.d` script with something like:
    - `sudo cp ./deploy/lumiere-client-lifx.init.d /etc/init.d/lumiere-client-lifx && sudo chmod +x /etc/init.d/lumiere-client-lifx`
- Update the script as needed. Mostly this will just be updating the `dir` variable to point where the code is installed.
- Install to be able to be run on startup.
    - `sudo update-rc.d lumiere-client-lifx defaults`



