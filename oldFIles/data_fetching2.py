import requests


class DataProvider:
    """
    Add class description here
    """

    def __init__(self):
        self.base_url = "https://disease.sh/v3/covid-19"

    def get_historical_data(self, country: str, window: int) -> dict[str, str]:
        """
        Add function description.
        """
        url = f"{self.base_url}/historical/{country}?lastdays={window}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return self._parse_historical_data(data)
        else:
            print(f"Error {response.status_code}: {response.text}")
            # Raise error
            response.raise_for_status()

    def fetch_latest_data(self, country: str) -> dict:
        """
        Add function description.
        """
        url = f"{self.base_url}/countries/{country}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return self._parse_latest_data(data)
        else:
            print(f"Error {response.status_code}: {response.text}")
            # Raise error
            response.raise_for_status()

    def _parse_historical_data(self, data):
        country = data["country"]
        timeline = data["timeline"]
        cases = timeline["cases"]
        deaths = timeline["deaths"]
        recovered = timeline["recovered"]

        historical_data = {
            "country": country,
            "cases": cases,
            "deaths": deaths,
            "recovered": recovered,
        }
        return historical_data

    def _parse_latest_data(self, data):
        latest_data = {
            "country": data["country"],
            "cases": data["cases"],
            "todayCases": data["todayCases"],
            "deaths": data["deaths"],
            "todayDeaths": data["todayDeaths"],
            "recovered": data["recovered"],
            "active": data["active"],
            "critical": data["critical"],
            "tests": data["tests"],
        }
        return latest_data


def get_raw_data(country):
    """
    Add function description.
    """
    data_provider_api = DataProvider()

    try:
        raw_data = data_provider_api.get_historical_data(country, 60)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred fetching the data: {req_err}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    return raw_data
