import logging
import requests
from random import shuffle
from os import getenv
import socketio
from pprint import pprint
from dotenv import load_dotenv

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

# Animation duration
log_level = int(getenv("LOG_LEVEL", 30))

# Logging
logging.basicConfig(level=log_level)
logger = logging.getLogger("lumiere-client-lifx")

# Auth
headers = {
    "Authorization": "Bearer %s" % getenv("LUMIERE_LIFX_API_KEY"),
}


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

    return lights


def update_lights(lights, colors):
    # TODO: Handle the possibility that there are a larger
    # number of lights and spread like we do in other clients.

    # Unique and randomize colors
    unique_colors = list(set(colors))
    shuffle(unique_colors)
    shuffled_colors = unique_colors

    # Go through each light
    for li, light in enumerate(lights):
        color = shuffled_colors[li % len(shuffled_colors) - 1]

        light_response = requests.put(
            "https://api.lifx.com/v1/lights/all/state",
            params={
                "selector": f'id:{light["id"]}',
                "color": color,
                "brightness": brightness,
                "duration": duration,
            },
            headers=headers,
        )

        # TODO: Handle issues
        # pprint(light_response.json())


if __name__ == "__main__":
    main_client()
