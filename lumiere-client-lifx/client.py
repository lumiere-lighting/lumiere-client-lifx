import json
import logging
from os import getenv
from random import shuffle

import requests
import socketio
from dotenv import load_dotenv
from tenacity import after_log, retry, stop_after_attempt, wait_fixed

# Load config
load_dotenv()

# What domain to connect to
api_domain = getenv("LUMIERE_API_DOMAIN", "https://api.lumiere.lighting")

# Which lights to get
lights_selector = getenv("LUMIERE_LIFX_LIGHTS", "all")

# Brightness
brightness = float(getenv("LUMIERE_LIFX_BRIGHTNESS", 0.85))

# Animation duration
duration = float(getenv("LUMIERE_LIFX_DURATION", 1))

# Shuffle
shuffle_lights = bool(getenv("LUMIERE_LIFX_SHUFFLE", False))

# Animation duration
log_level = int(getenv("LOG_LEVEL", 30))

# Logging
logging.basicConfig(level=log_level)
logger = logging.getLogger("lumiere-client-lifx")

# Auth
headers = {
    "Authorization": "Bearer %s" % getenv("LUMIERE_LIFX_API_KEY"),
}


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(5),
    after=after_log(logger, logging.DEBUG),
)
def main_client():
    # Get all lights
    all_lights = get_all_lights()

    # SocketIO client
    sio = socketio.Client()

    # Socket on connection
    @sio.event
    def connect():
        logger.info("connection established")

        # Get lights on connection
        sio.emit("lights:get")

    # Socket lights event
    @sio.event
    def lights(lumiere_lights):
        update_lights(all_lights, lumiere_lights["colors"])

    # Socket disconnect
    @sio.event
    def disconnect():
        logger.info("disconnected from server")

    # Connect to server
    sio.connect(api_domain)
    sio.wait()


def get_all_lights():
    # Get list of lights
    lights_response = requests.get(
        "https://api.lifx.com/v1/lights/all",
        params={"selector": lights_selector},
        headers=headers,
    )

    # TODO: Handle issues
    # response.status_code
    # response.headers['X-RateLimit-Remaining'] <= 0

    lights = lights_response.json()

    # Check issues
    if lights_response.status_code >= 300:
        # Not right error
        raise ValueError(
            f"Error calling LIFX, response: '{lights_response.status_code}', message: {lights.get('error', 'unknown error')}"
        )

    # Order lights by name
    return sorted(lights, key=lambda item: item["label"])


def get_current_colors():
    # Get current lumiere lights
    lumiere_response = requests.get(f"{api_domain}/lights/current")
    lumiere_lights = lumiere_response.json()
    return lumiere_lights["results"]["colors"]


def update_lights(lights, colors):
    # TODO: Handle the possibility that there are a larger
    # number of lights and spread like we do in other clients.

    # Unique colors
    unique_colors = list(dict.fromkeys(colors))

    # Shuffle/randomize or use in order
    if shuffle_lights:
        shuffle(unique_colors)
        ordered_colors = unique_colors
    else:
        ordered_colors = unique_colors

    # Go through each light and add to payload
    payload = []
    for li, light in enumerate(lights):
        light_index = li % len(ordered_colors)
        color = ordered_colors[light_index]
        payload.append(
            {
                "selector": f"id:{light['id']}",
                "color": color,
                "brightness": brightness,
                "duration": duration,
            }
        )

    # Make ccall to update all lights
    payload = {
        "states": payload,
    }
    light_response = requests.put(
        "https://api.lifx.com/v1/lights/states",
        data=json.dumps(payload),
        headers=headers,
    )

    # Handle issues
    light_data = light_response.json()
    if light_response.status_code >= 300:
        # Not right error
        raise ValueError(
            f"Error calling LIFX, response: '{light_response.status_code}', message: {light_data.get('error', 'unknown error')}"
        )


if __name__ == "__main__":
    main_client()
