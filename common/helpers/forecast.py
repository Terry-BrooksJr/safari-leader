from typing import Any, Dict, Optional

import requests


class WeatherMan:
    """Provide utility methods for resolving weather-related data.

    This class encapsulates helpers to extract client IP addresses, derive
    geolocation information, and obtain weather forecast URLs for given
    coordinates.
    """

    @classmethod
    def get_client_ip(cls, request):
        """Retrieve the client's IP address from a Django request object.

        This function checks for a forwarded-for header first, falling back to the
        remote address when a proxy header is not present.

        Args:
            request: The Django HTTP request object containing META headers.

        Returns:
            str: The IP address of the client extracted from the request.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        return (
            x_forwarded_for.split(",")[0].strip()
            if x_forwarded_for
            else request.META.get("REMOTE_ADDR")
        )

    @classmethod
    def get_geographic_data(cls, ip: str) -> Dict[str, Any]:
        """Resolve geolocation coordinates and metadata for an IP address.

        This function queries an external IP geolocation service and returns
        structured location data when the lookup is successful.

        Args:
            ip: The IP address to geolocate.

        Returns:
            Dict[str, Any]: A dictionary containing location metadata such as
            latitude, longitude, city, region, and country, or an empty dict if
            the lookup fails or the IP is local.
        """
        response = requests.get(f"https://ipwho.is/{ip}")
        if response.status_code != 200:
            return {}
        data = response.json()
        if ip in {"0.0.0.0", "127.0.0.1", "localhost"}:
            return {}
        return {
            "ip": ip,
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "city": data["city"],
            "region": data["region"],
            "country": data["country"],
        }

    @classmethod
    def get_forecast(cls, geographic_data: Dict[str, Any]) -> Optional[str]:
        """Build a forecast URL using geographic coordinate data.

        This function validates latitude and longitude values and attempts to
        obtain a forecast URL for the given location.

        Args:
            geographic_data: A mapping containing at least `latitude` and
                `longitude` keys used to locate the weather forecast.

        Returns:
            Optional[str]: The hourly forecast URL string if it can be resolved,
            otherwise None when the coordinates are invalid or a lookup error
            occurs.
        """
        longitude = geographic_data["longitude"]
        latitude = geographic_data["latitude"]

        if not latitude or not longitude:
            print("Invalid coordinates provided")
            return None

        try:
            return cls.get_forcaset_url(latitude, longitude)
        except Exception as error:
            print(f"Unable to get forecast URL: {error}")
            return None

    @classmethod
    def get_forcaset_url(cls, latitude: int, longitude: int) -> str:
        """Retrieve the hourly weather forecast URL for a given latitude and longitude.

        This function queries the National Weather Service API and returns a URL
        that can be used to obtain hourly forecast data for the specified location.

        Args:
            latitude: The latitude of the location to fetch forecast data for.
            longitude: The longitude of the location to fetch forecast data for.

        Returns:
            Optional[str]: The URL for the hourly weather forecast if available,
            otherwise None when the grid is not found or an HTTP error occurs.
        """
        url = f"https://api.weather.gov/points/{latitude},{longitude}"
        print(url)
        response = requests.get(url)
        if response.status_code == 404:
            print(f"No weather grid found for location: {latitude}, {longitude}")
            return None

        if not response.ok:
            print(f"Error: {response.status_code}")
            return None

        data = response.json()
        return data["properties"]["forecastHourly"]

    @classmethod
    def getWeatherData(cls, geo_data, forecast_url) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(forecast_url)

            if not response.ok:
                print(f"Error: {response.status_code}")

            data = response.json()
            return cls.parse_weather_data(geo_data, data["properties"]["periods"][0])
        except Exception as error:
            print(f"Unable to get weather data: {error}")

    @classmethod
    def parse_weather_data(
        cls, coordinates: Dict[str, Any], weather_data: Dict[str, Any]
    ):
        return {
            "city": coordinates["city"],
            "region": coordinates["region"],
            "shortForecast": weather_data["shortForecast"],
            "temp": f"{weather_data['temperature']}°{weather_data["temperatureUnit"]}",
            "icon": weather_data["icon"],
        }

    @classmethod
    def forecast(cls, request):
        """Generate a weather forecast summary for the client making the request.

        This method resolves the client's IP address, derives geolocation data,
        and returns parsed forecast information for that location.

        Args:
            request: The Django HTTP request used to determine the client's IP.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing summarized weather
            data for the client's location, or None if the forecast cannot be
            retrieved.
        """
        ip = cls.get_client_ip(request)
        geo_data = cls.get_geographic_data(ip)
        return cls.getWeatherData(geo_data, cls.get_forecast(geo_data))
