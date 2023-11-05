from datetime import datetime
from enum import Enum
from typing import Any, Optional

import requests

from .units import celsius_to_fahrenheit

__all__ = ["Weather"]


class Weather:
    """Wrapper around the weather.gov API that uses a station code to read observations."""
    API_LINK = "https://api.weather.gov"

    def __init__(self, station_code: str):
        self.station_code = station_code

    def retrieve_observation(self, time: Optional[datetime] = None) -> dict[str, Any]:
        """Retrieves an observation from the station code provided.

        :param time: The time to retrieve the observation for (uses the latest observation if time is None).
        :return: A dictionary containing the value for each datapoint as per the observation.
        """
        if time is None:
            response = requests.get(f"{self.API_LINK}/stations/{self.station_code}/observations/latest").json()
            weather_data = response["properties"]
        else:
            response = requests.get(
                url=f"{self.API_LINK}/stations/{self.station_code}/observations",
                params={"start": time.isoformat()}
            ).json()
            weather_data = response["features"][-1]["properties"]  # Gets closest observation to the time given

        return {
            "raw_time": datetime.fromisoformat(weather_data["timestamp"]),
            "time_fmt": (
                datetime.fromisoformat(weather_data["timestamp"])
                    .astimezone(tz=None)
                    .strftime("%I:%M %p")
                    .strip("0")
            ),
            "temperature": round(celsius_to_fahrenheit(weather_data["temperature"]["value"]), 1),
            "dewpoint": round(celsius_to_fahrenheit(weather_data["dewpoint"]["value"]), 1),
            "relative_humidity": round(weather_data["relativeHumidity"]["value"], 0)
        }
