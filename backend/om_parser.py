import openmeteo_requests
import requests_cache
import datetime
from datetime import datetime as dt
from retry_requests import retry


class omParser:
    def __init__(self, lat: str, long: str) -> None:
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.params = {
            "latitude": float(lat),
            "longitude": float(long),
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "is_day",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ],
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
            ],
            "timezone": "auto",
            "forecast_days": 5,
        }
        pass

    def weather_code_name(self, weather_code: int) -> str:
        c_wc = "Unknown"

        match weather_code:
            case 0:
                c_wc = "Clear Sky"
            case 1:
                c_wc = "Mainly Clear"
            case 2:
                c_wc = "Partly Cloudy"
            case 3:
                c_wc = "Overcast"
            case 45:
                c_wc = "Fog"
            case 48:
                c_wc = "Rime Fog"  # Poladovica
            case 51:
                c_wc = "Light Drizzle"
            case 53:
                c_wc = "Moderate Drizzle"
            case 55:
                c_wc = "Dense Drizzle"
            case 56:
                c_wc = "Light Freezing Drizzle"
            case 57:
                c_wc = "Dense Freezing Drizzle"
            case 61:
                c_wc = "Slight Rain"
            case 63:
                c_wc = "Moderate Rain"
            case 65:
                c_wc = "Heavy Rain"
            case 66:
                c_wc = "Light Freezing Rain"
            case 67:
                c_wc = "Heavy Freezing Rain"
            case 71:
                c_wc = "Slight Snow Fall"
            case 73:
                c_wc = "Moderate Snow Fall"
            case 75:
                c_wc = "Heavy Snow Fall"
            case 77:
                c_wc = "Snow Grains"
            case 80:
                c_wc = "Slight Rain Showers"
            case 81:
                c_wc = "Moderate Rain Showers"
            case 82:
                c_wc = "Violent Rain Showers"
            case 85:
                c_wc = "Slight Snow Showers"
            case 86:
                c_wc = "Heavy Snow Showers"
            case 95:
                c_wc = "Thunderstorm"
            case 96:
                c_wc = "Thunderstorm with Slight Hail"
            case 99:
                c_wc = "Thunderstorm with Heavy Hail"
        return c_wc

    def update(self) -> dict:
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        responses = openmeteo.weather_api(self.url, params=self.params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        c_elev = response.Elevation()
        c_timezone = response.TimezoneAbbreviation().decode("utf-8")

        current = response.Current()
        c_temp = round(current.Variables(0).Value(), 1)
        c_rel_humidity = round(current.Variables(1).Value())
        c_is_day = bool(current.Variables(2).Value())
        c_prec = round(current.Variables(3).Value(), 1)
        c_weather_code = int(current.Variables(4).Value())
        c_wind_speed = round(current.Variables(5).Value(), 1)
        c_wind_dir = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][
            int((current.Variables(6).Value() / 45) + 0.5) % 8
        ]
        c_wind_gusts = round(current.Variables(7).Value(), 1)
        c_date = dt.today().strftime("%d/%m")
        c_time = dt.today().strftime("%H:%M:%S")

        c_weather = {
            "elevation": c_elev,
            "timezone": c_timezone,
            "date": c_date,
            "time": c_time,
            "is-day": c_is_day,
            "temperature": c_temp,
            "precipitation": c_prec,
            "rel-humidity": c_rel_humidity,
            "wind-speed": c_wind_speed,
            "wind-gusts": c_wind_gusts,
            "wind-dir": c_wind_dir,
            "weather-code": [c_weather_code, self.weather_code_name(c_weather_code)],
        }

        daily = response.Daily()
        today = dt.today()
        daily_date = [
            (today + datetime.timedelta(days=1)).strftime("%d/%m"),
            (today + datetime.timedelta(days=2)).strftime("%d/%m"),
            (today + datetime.timedelta(days=3)).strftime("%d/%m"),
        ]
        daily_weather_code = daily.Variables(0).ValuesAsNumpy().astype(int).tolist()[2:]
        daily_temperature_2m_max = [
            round(x, 1) for x in daily.Variables(1).ValuesAsNumpy().tolist()
        ][2:]
        daily_temperature_2m_min = [
            round(x, 1) for x in daily.Variables(2).ValuesAsNumpy().tolist()
        ][2:]
        daily_precipitation_sum = [
            round(x, 1) for x in daily.Variables(3).ValuesAsNumpy().tolist()
        ][2:]

        daily_dict = {}
        for i in range(3):
            daily_dict[str(i)] = {
                "date": daily_date[i],
                "code": [
                    daily_weather_code[i],
                    self.weather_code_name(int(daily_weather_code[i])),
                ],
                "temp-max": daily_temperature_2m_max[i],
                "temp-min": daily_temperature_2m_min[i],
                "prec": daily_precipitation_sum[i],
            }

        forecast = {"current": c_weather, "daily": daily_dict}

        return forecast

    def relocate(self, lat: str, long: str) -> None:
        "Change location to different coords"
        self.params = {
            "latitude": float(lat),
            "longitude": float(long),
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "is_day",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ],
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
            ],
            "timezone": "auto",
            "forecast_days": 3,
        }
