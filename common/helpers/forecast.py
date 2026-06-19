from typing import Any, Dict, Optional, Union
from loguru import logger 
import requests


class WeatherMan:
    """Provide utility methods for resolving weather-related data.

    This class encapsulates helpers to extract client IP addresses, derive
    geolocation information, and obtain weather forecast URLs for given
    coordinates.
    """

    @classmethod
    def get_client_ip(cls, request) -> str:
        """Retrieve the client's IP address from a Django request object.

        This function checks for a forwarded-for header first, falling back to the
        remote address when a proxy header is not present.

        Args:
            request: The Django HTTP request object containing META headers.

        Returns:
            str: The IP address of the client extracted from the request.
        """
        try:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.META.get("REMOTE_ADDR")
            if ip is None:
                logger.warning('No IP address available in request headers')
                return "0.0.0.0"
            logger.success('Successfully Captured User IP Address for Weather Forecasting')
            return str(ip)
        except Exception as e: 
            logger.warning(f'Error: Unable to Capture User IP Address for Weather Forcasting: {e}')
            return "0.0.0.0"

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
        try:
            if ip in {"0.0.0.0", "127.0.0.1", "localhost"}:
                logger.warning(f"Error: Invalid or Local IP Address Provided. Unable to Forecast: {ip}")
                return {}
            response = requests.get(f"https://ipwho.is/{ip}", timeout=5)
            if response.status_code != 200:
                return {}
            data = response.json()
            geo_data = {
                "ip": ip,
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "city": data["city"],
                "region": data["region"],
                "country": data["country"],
            }
            logger.success('Successfully Queried User IP Address for Geographic Data')
            return geo_data
        except Exception as e: 
            logger.warning(f'Error: Unable to Query User IP Address for Geographic Data: {e}')
            return {}

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
        longitude = geographic_data.get("longitude")
        latitude = geographic_data.get("latitude")

        if not latitude or not longitude:
            logger.error("Error: Invalid coordinates provided")
            return None

        try:
            return cls.get_forcaset_url(latitude, longitude)
        except Exception as error:
            logger.warning(f"Unable to get forecast URL: {error}")
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
        try: 
            url = f"https://api.weather.gov/points/{latitude},{longitude}"
            response = requests.get(url, timeout=5)
            if response.status_code == 404:
                logger.warning(f"No weather grid found for location: {latitude}, {longitude}")
                return None

            if not response.ok:
                logger.error(f"HTTP Error: {response.status_code}")
                return None

            data = response.json()
            return data["properties"]["forecastHourly"]
        except Exception as e: 
            logger.warning(f"Error: {str(e)}")

    @classmethod
    def getWeatherData(cls, geo_data, forecast_url) -> Dict[str, Any]:
        try:
            response = requests.get(forecast_url, timeout=5)

            if not response.ok:
                logger.warning(f"Error: {response.status_code}")
                return {}

            data = response.json()
            return cls.parse_weather_data(geo_data, data["properties"]["periods"][0])
        except Exception as error:
            logger.warning(f"Unable to get weather data: {error}")
            return {}

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
    def forecast(cls, request) -> Dict[str, Any]:
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
        logger.debug('Beginning Server Side Weather Forecasting...')
        ip = cls.get_client_ip(request)
        if ip != "0.0.0.0":
            geo_data = cls.get_geographic_data(ip)
            if geo_data != {}:
                logger.debug("Successfully Collected IP address and Geographic Data...")
                results = cls.getWeatherData(geo_data, cls.get_forecast(geo_data))
                if results != {}:
                    logger.success("Successfully Obtained and Parsed Weather Data!")
                    return results
        logger.error('Server Side Weather Forecasting Failed!')
        return {}
        
