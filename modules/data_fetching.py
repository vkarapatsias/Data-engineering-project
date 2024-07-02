from datetime import datetime, timedelta
import requests
from config.config import SCHIPHOL_API_APP_ID, SCHIPHOL_API_APP_KEY, DATA_WINDOW_HOURS
from config.logging_config import logger


class SchipholDataFetcher:
    """
    Class to handle data fetching from Schiphol API.
    """

    def __init__(self):
        self.base_url = "https://api.schiphol.nl/public-flights"
        self.headers = {
            "Accept": "application/json",
            "app_id": SCHIPHOL_API_APP_ID,
            "app_key": SCHIPHOL_API_APP_KEY,
            "ResourceVersion": "v4",
        }
        self.logger = logger

    def _fetch_data_from_api(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 204:
                self.logger.warning(
                    f"No content returned from {endpoint} for params {params}"
                )
                return None
            response.raise_for_status()
            self.logger.debug(f"Data fetched successfully from {endpoint}")
            return response.json()
        except requests.exceptions.HTTPError as errh:
            self.logger.error(f"Http Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            self.logger.error(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            self.logger.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Error: {err}")
        return None

    def _fetch_pages_iteratively(self, endpoint, params=None):
        all_data = []
        page = 0

        while True:
            params["page"] = page
            data = self._fetch_data_from_api(endpoint, params)
            if data is not None:
                all_data.extend(data["flights"])
            else:
                break

            page += 1
            if page > 50:
                # Setting upper threshold 50 for page size (for simplicity)
                break
        return all_data

    def fetch_flights_data(self, fromDatetime: str, toDatetime: str):
        """
        Function that fetches the flight data the window defined by the arguments.
        """
        params = {
            "includedelays": "true",
            "sort": "+scheduleTime",
            "fromDateTime": fromDatetime,
            "toDateTime": toDatetime,
        }

        return self._fetch_pages_iteratively("flights", params)

    def fetch_airlines_data(self, airline: str):
        return self._fetch_data_from_api("airlines/" + airline)

    def fetch_destinations_data(self, iata: str):
        return self._fetch_data_from_api("destinations/" + iata)


def fetch_flights_data(window_hours=-1) -> tuple[list, str]:
    """
    Exposed function that fetches the flight entries. Optional argument window
    defines the time window for which we request data.
    """
    api_fetcher = SchipholDataFetcher()

    # Define the time window
    now = datetime.now()
    if window_hours < 0:
        window_hours = DATA_WINDOW_HOURS
    offset_datetime = now - timedelta(hours=window_hours)

    # Format the datetime as a string in the desired format
    fromDatetime = offset_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    toDatetime = now.strftime("%Y-%m-%dT%H:%M:%S")

    try:
        logger.debug("Requesting flight data...")
        flights = api_fetcher.fetch_flights_data(
            fromDatetime, toDatetime
        )
        logger.debug("Fetched flight data successfully.")
    except Exception as err:
        logger.error(f"Error: {err}")

    return [flights, toDatetime + "_" + fromDatetime]


def fetch_airline(airline: str) -> dict:
    """
    Exposed function that returns airline's information.
    """
    api_fetcher = SchipholDataFetcher()
    try:
        logger.debug("Requesting airline info...")
        airline = api_fetcher.fetch_airlines_data(airline)
        logger.debug("Fetched airline info successfully.")

    except Exception as err:
        logger.error(f"Error: {err}")

    return airline


def fetch_destination(iata: str) -> dict:
    """
    Exposed function that returns destination's information.
    """
    api_fetcher = SchipholDataFetcher()
    try:
        logger.debug("Requesting destination info...")
        destination = api_fetcher.fetch_destinations_data(iata)
        logger.debug("Fetched destination info successfully.")
    except Exception as err:
        logger.error(f"Error: {err}")

    return destination
