"""Unit tests for :mod:`common.helpers.forecast`.

All external HTTP traffic is mocked: ``requests`` is patched at the module
level so no real calls to ipwho.is or api.weather.gov are made. Tests cover
both the happy paths and every failure branch of ``WeatherMan``, including the
``loguru``-logged guard clauses that return sentinel values (``"0.0.0.0"`` /
``{}`` / ``None``) instead of raising.
"""

from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from common.helpers.forecast import WeatherMan


def _response(status_code=200, json_data=None, ok=None):
    """Build a stand-in for a ``requests.Response``.

    ``ok`` mirrors ``requests`` semantics, truthy for status < 400, unless an
    explicit value is supplied.
    """
    resp = Mock()
    resp.status_code = status_code
    resp.ok = (status_code < 400) if ok is None else ok
    resp.json.return_value = {} if json_data is None else json_data
    return resp


# ─── get_client_ip ──────────────────────────────────────────────────────────


class GetClientIpTest(SimpleTestCase):
    """Verify client IP resolution from request META headers."""

    @staticmethod
    def _request(meta):
        return Mock(META=meta)

    def test_uses_forwarded_for_when_present(self):
        request = self._request(
            {"HTTP_X_FORWARDED_FOR": "203.0.113.7", "REMOTE_ADDR": "10.0.0.1"}
        )
        self.assertEqual(WeatherMan.get_client_ip(request), "203.0.113.7")

    def test_returns_first_ip_from_forwarded_chain(self):
        request = self._request(
            {"HTTP_X_FORWARDED_FOR": "203.0.113.7, 70.41.3.18, 150.172.238.178"}
        )
        self.assertEqual(WeatherMan.get_client_ip(request), "203.0.113.7")

    def test_strips_whitespace_from_forwarded_ip(self):
        request = self._request(
            {"HTTP_X_FORWARDED_FOR": "  203.0.113.7  , 10.0.0.1"}
        )
        self.assertEqual(WeatherMan.get_client_ip(request), "203.0.113.7")

    def test_falls_back_to_remote_addr_without_forwarded_header(self):
        request = self._request({"REMOTE_ADDR": "10.0.0.1"})
        self.assertEqual(WeatherMan.get_client_ip(request), "10.0.0.1")

    def test_empty_forwarded_header_falls_back_to_remote_addr(self):
        request = self._request(
            {"HTTP_X_FORWARDED_FOR": "", "REMOTE_ADDR": "10.0.0.1"}
        )
        self.assertEqual(WeatherMan.get_client_ip(request), "10.0.0.1")

    def test_returns_zero_ip_when_no_ip_available(self):
        request = self._request({})
        self.assertEqual(WeatherMan.get_client_ip(request), "0.0.0.0")

    def test_returns_zero_ip_on_exception(self):
        broken_meta = Mock()
        broken_meta.get.side_effect = RuntimeError("boom")
        request = Mock(META=broken_meta)
        self.assertEqual(WeatherMan.get_client_ip(request), "0.0.0.0")


# ─── get_geographic_data ────────────────────────────────────────────────────


@patch("common.helpers.forecast.requests")
class GetGeographicDataTest(SimpleTestCase):
    """Verify IP geolocation lookups and their guard clauses."""

    DATA = {
        "latitude": 47.6062,
        "longitude": -122.3321,
        "city": "Seattle",
        "region": "Washington",
        "country": "United States",
    }

    def test_returns_structured_location_on_success(self, mock_requests):
        mock_requests.get.return_value = _response(200, self.DATA)

        result = WeatherMan.get_geographic_data("8.8.8.8")

        self.assertEqual(
            result,
            {
                "ip": "8.8.8.8",
                "latitude": 47.6062,
                "longitude": -122.3321,
                "city": "Seattle",
                "region": "Washington",
                "country": "United States",
            },
        )

    def test_queries_ipwhois_endpoint_with_timeout(self, mock_requests):
        mock_requests.get.return_value = _response(200, self.DATA)

        WeatherMan.get_geographic_data("8.8.8.8")

        mock_requests.get.assert_called_once_with(
            "https://ipwho.is/8.8.8.8", timeout=5
        )

    def test_returns_empty_dict_on_non_200_status(self, mock_requests):
        mock_requests.get.return_value = _response(500, {})
        self.assertEqual(WeatherMan.get_geographic_data("8.8.8.8"), {})

    def test_returns_empty_dict_on_request_exception(self, mock_requests):
        mock_requests.get.side_effect = ConnectionError("network down")
        self.assertEqual(WeatherMan.get_geographic_data("8.8.8.8"), {})

    def test_loopback_ip_short_circuits_before_request(self, mock_requests):
        self.assertEqual(WeatherMan.get_geographic_data("127.0.0.1"), {})
        mock_requests.get.assert_not_called()

    def test_unspecified_ip_short_circuits_before_request(self, mock_requests):
        self.assertEqual(WeatherMan.get_geographic_data("0.0.0.0"), {})
        mock_requests.get.assert_not_called()

    def test_localhost_short_circuits_before_request(self, mock_requests):
        self.assertEqual(WeatherMan.get_geographic_data("localhost"), {})
        mock_requests.get.assert_not_called()


# ─── get_forecast ───────────────────────────────────────────────────────────


class GetForecastTest(SimpleTestCase):
    """Verify coordinate validation and delegation to ``get_forcaset_url``."""

    GEO = {"latitude": 47.6062, "longitude": -122.3321}

    def test_returns_url_for_valid_coordinates(self):
        with patch.object(
            WeatherMan,
            "get_forcaset_url",
            return_value="https://api.weather.gov/hourly",
        ) as mock_url:
            result = WeatherMan.get_forecast(self.GEO)

        self.assertEqual(result, "https://api.weather.gov/hourly")
        mock_url.assert_called_once_with(47.6062, -122.3321)

    def test_returns_none_when_latitude_is_falsy(self):
        result = WeatherMan.get_forecast({"latitude": 0, "longitude": -122.3321})
        self.assertIsNone(result)

    def test_returns_none_when_longitude_is_falsy(self):
        result = WeatherMan.get_forecast({"latitude": 47.6062, "longitude": 0})
        self.assertIsNone(result)

    def test_returns_none_when_url_lookup_raises(self):
        with patch.object(
            WeatherMan, "get_forcaset_url", side_effect=RuntimeError("boom")
        ):
            self.assertIsNone(WeatherMan.get_forecast(self.GEO))

    def test_returns_none_when_coordinates_missing(self):
        self.assertIsNone(WeatherMan.get_forecast({}))


# ─── get_forcaset_url ───────────────────────────────────────────────────────


@patch("common.helpers.forecast.requests")
class GetForecastUrlTest(SimpleTestCase):
    """Verify National Weather Service point lookups."""

    POINTS = {"properties": {"forecastHourly": "https://api.weather.gov/hourly"}}

    def test_returns_hourly_forecast_url_on_success(self, mock_requests):
        mock_requests.get.return_value = _response(200, self.POINTS)

        result = WeatherMan.get_forcaset_url(47.6062, -122.3321)

        self.assertEqual(result, "https://api.weather.gov/hourly")

    def test_queries_weather_points_endpoint_with_timeout(self, mock_requests):
        mock_requests.get.return_value = _response(200, self.POINTS)

        WeatherMan.get_forcaset_url(47.6062, -122.3321)

        mock_requests.get.assert_called_once_with(
            "https://api.weather.gov/points/47.6062,-122.3321",
            timeout=5,
        )

    def test_returns_none_on_404(self, mock_requests):
        mock_requests.get.return_value = _response(404, {})
        self.assertIsNone(WeatherMan.get_forcaset_url(0, 0))

    def test_returns_none_on_server_error(self, mock_requests):
        mock_requests.get.return_value = _response(500, {}, ok=False)
        self.assertIsNone(WeatherMan.get_forcaset_url(47.6062, -122.3321))

    def test_returns_none_on_request_exception(self, mock_requests):
        mock_requests.get.side_effect = ConnectionError("network down")
        self.assertIsNone(WeatherMan.get_forcaset_url(47.6062, -122.3321))


# ─── getWeatherData ─────────────────────────────────────────────────────────


@patch("common.helpers.forecast.requests")
class GetWeatherDataTest(SimpleTestCase):
    """Verify fetching and parsing of the hourly forecast payload."""

    GEO = {"city": "Seattle", "region": "Washington"}
    PAYLOAD = {
        "properties": {
            "periods": [
                {
                    "shortForecast": "Sunny",
                    "temperature": 72,
                    "temperatureUnit": "F",
                    "icon": "https://api.weather.gov/icons/sunny",
                }
            ]
        }
    }

    def test_returns_parsed_weather_on_success(self, mock_requests):
        mock_requests.get.return_value = _response(200, self.PAYLOAD)

        result = WeatherMan.getWeatherData(self.GEO, "https://api.weather.gov/hourly")

        self.assertEqual(
            result,
            {
                "city": "Seattle",
                "region": "Washington",
                "shortForecast": "Sunny",
                "temp": "72°F",
                "icon": "https://api.weather.gov/icons/sunny",
            },
        )

    def test_requests_the_supplied_forecast_url_with_timeout(self, mock_requests):
        mock_requests.get.return_value = _response(200, self.PAYLOAD)

        WeatherMan.getWeatherData(self.GEO, "https://api.weather.gov/hourly")

        mock_requests.get.assert_called_once_with(
            "https://api.weather.gov/hourly",
            timeout=5,
        )

    def test_returns_empty_dict_when_response_not_ok(self, mock_requests):
        mock_requests.get.return_value = _response(500, {}, ok=False)
        self.assertEqual(WeatherMan.getWeatherData(self.GEO, "url"), {})

    def test_returns_empty_dict_when_request_raises(self, mock_requests):
        mock_requests.get.side_effect = ConnectionError("network down")

        self.assertEqual(
            WeatherMan.getWeatherData(self.GEO, "https://api.weather.gov/hourly"),
            {},
        )

    def test_returns_empty_dict_on_malformed_payload(self, mock_requests):
        mock_requests.get.return_value = _response(200, {"properties": {}})

        self.assertEqual(WeatherMan.getWeatherData(self.GEO, "url"), {})


# ─── parse_weather_data ─────────────────────────────────────────────────────


class ParseWeatherDataTest(SimpleTestCase):
    """Verify the summary dict shape and temperature formatting."""

    def test_builds_summary_dict(self):
        coordinates = {"city": "Seattle", "region": "Washington"}
        weather = {
            "shortForecast": "Partly Cloudy",
            "temperature": 68,
            "temperatureUnit": "F",
            "icon": "https://api.weather.gov/icons/cloudy",
        }

        result = WeatherMan.parse_weather_data(coordinates, weather)

        self.assertEqual(
            result,
            {
                "city": "Seattle",
                "region": "Washington",
                "shortForecast": "Partly Cloudy",
                "temp": "68°F",
                "icon": "https://api.weather.gov/icons/cloudy",
            },
        )

    def test_formats_temperature_with_unit(self):
        result = WeatherMan.parse_weather_data(
            {"city": "X", "region": "Y"},
            {
                "shortForecast": "Cold",
                "temperature": -5,
                "temperatureUnit": "C",
                "icon": "i",
            },
        )

        self.assertEqual(result["temp"], "-5°C")


# ─── forecast orchestration ─────────────────────────────────────────────────


class ForecastOrchestrationTest(SimpleTestCase):
    """Verify ``forecast`` wires the helper methods together and short-circuits."""

    def test_wires_helpers_together(self):
        request = Mock()
        geo = {"latitude": 1, "longitude": 2}

        with patch.object(
            WeatherMan, "get_client_ip", return_value="8.8.8.8"
        ) as mock_ip, patch.object(
            WeatherMan, "get_geographic_data", return_value=geo
        ) as mock_geo, patch.object(
            WeatherMan, "get_forecast", return_value="hourly-url"
        ) as mock_forecast, patch.object(
            WeatherMan, "getWeatherData", return_value={"temp": "72°F"}
        ) as mock_weather:
            result = WeatherMan.forecast(request)

        self.assertEqual(result, {"temp": "72°F"})
        mock_ip.assert_called_once_with(request)
        mock_geo.assert_called_once_with("8.8.8.8")
        mock_forecast.assert_called_once_with(geo)
        mock_weather.assert_called_once_with(geo, "hourly-url")

    def test_returns_empty_dict_when_ip_unavailable(self):
        request = Mock()

        with (
            patch.object(WeatherMan, "get_client_ip", return_value="0.0.0.0"),
            patch.object(WeatherMan, "get_geographic_data") as mock_geo,
        ):
            result = WeatherMan.forecast(request)

        self.assertEqual(result, {})
        mock_geo.assert_not_called()

    def test_returns_empty_dict_when_geo_lookup_fails(self):
        request = Mock()

        with (
            patch.object(WeatherMan, "get_client_ip", return_value="8.8.8.8"),
            patch.object(WeatherMan, "get_geographic_data", return_value={}),
            patch.object(WeatherMan, "getWeatherData") as mock_weather,
        ):
            result = WeatherMan.forecast(request)

        self.assertEqual(result, {})
        mock_weather.assert_not_called()

    def test_returns_empty_dict_when_weather_data_empty(self):
        request = Mock()
        geo = {"latitude": 1, "longitude": 2}

        with (
            patch.object(WeatherMan, "get_client_ip", return_value="8.8.8.8"),
            patch.object(WeatherMan, "get_geographic_data", return_value=geo),
            patch.object(WeatherMan, "get_forecast", return_value="hourly-url"),
            patch.object(WeatherMan, "getWeatherData", return_value={}),
        ):
            result = WeatherMan.forecast(request)

        self.assertEqual(result, {})