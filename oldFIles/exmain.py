import json
from datetime import datetime

from data_fetch import get_schiphol_flights_data


def load_config():
    config_file = "config.json"
    with open(config_file, "r") as file:
        config = json.load(file)
    return config


def main():
    """
    This is the main function
    """
    today_date = datetime.today().strftime("%Y-%m-%d")
    today_flights_data = get_schiphol_flights_data(load_config(), today_date)

    if today_flights_data:
        print("Flights Data:")
        print(json.dumps(today_flights_data, indent=2))
    else:
        print(f"No flights data available for {today_flights_data}.")


if __name__ == "__main__":
    main()
