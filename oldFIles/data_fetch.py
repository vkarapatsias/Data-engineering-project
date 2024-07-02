import requests


class SchipholAirportAPI:
    """
    Schiphol airport API class
    """

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key
        self.base_url = "https://api.schiphol.nl/public-flights/"

    def fetch_flights_data(self, flight_date):
        """
        Function to fetch the flight data

        Args:
            - flight_date
        """
        url = f"{self.base_url}flights"
        headers = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "ResourceVersion": "v4",
            "Accept": "application/json",
        }
        params = {
            "includedelays": "false",  # Convert to lowercase string
            "page": "0",
            "sort": "+scheduleTime",
            "scheduledate": flight_date,
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            print(f"No flights found for the date {flight_date}.")
            return None
        else:
            print(f"Error {response.status_code}: {response.text}")
            response.raise_for_status()

    def _parse_flights_data(self, data):
        flights = data.get("flights", [])
        if not flights:
            return None
        flights_data = []
        for flight in flights:
            flight_info = {
                "flightName": flight.get("flightName"),
                "scheduleDate": flight.get("scheduleDate"),
                "scheduleTime": flight.get("scheduleTime"),
                "estimatedLandingTime": flight.get("estimatedLandingTime"),
                "actualLandingTime": flight.get("actualLandingTime"),
                "status": (
                    flight["publicFlightState"]["flightStates"][0]
                    if flight.get("publicFlightState")
                    else "Unknown"
                ),
            }
            flights_data.append(flight_info)
        return flights_data


def get_schiphol_flights_data(config, flight_date):
    """
    Fetch raw data from the Schiphol class
    """
    app_id = config["app_id"]
    app_key = config["app_key"]
    schiphol_api = SchipholAirportAPI(app_id, app_key)
    try:
        flights_data = schiphol_api.fetch_flights_data(flight_date)
        return flights_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
