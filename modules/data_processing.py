import pandas as pd
from collections import Counter

from data_fetching import fetch_airline, fetch_destination
from config.config import SCHEMA_VERSION
from config.logging_config import logger


def cleanup_flight_data(flight_data: list) -> tuple[list, list]:
    """
    Method to clean up the raw data and separate departures and arrivals.
    """
    departures_cleaned = []
    arrivals_cleaned = []
    for flight in flight_data:
        if flight["schemaVersion"] != SCHEMA_VERSION:
            raise Exception(
                "Schema version of the API has changed from "
                + str(SCHEMA_VERSION)
                + " to "
                + str(flight["schemaVersion"])
            )

        processed_flight = {
            # General
            "flight_name": flight["flightName"],
            "terminal": flight["terminal"] if "terminal" in flight.keys() else "",
            # Keep the most recent entry only
            "publicFlightState": flight["publicFlightState"]["flightStates"][0],
            # Destination
            "route": flight["route"],
            # Company info
            "flight_company_prefix": (
                flight["prefixICAO"] if "prefixICAO" in flight.keys() else ""
            ),
            # Aircraft info
            "aircraftType": (
                flight["aircraftType"] if "aircraftType" in flight.keys() else ""
            ),
        }
        if flight["flightDirection"] == "A":
            # Arrivals
            processed_flight["arrivalInfo"] = {
                "estimatedLandingTime": (
                    flight["estimatedLandingTime"]
                    if "estimatedLandingTime" in flight.keys()
                    else ""
                ),
                "actualLandingTime": (
                    flight["actualLandingTime"]
                    if "actualLandingTime" in flight.keys()
                    else ""
                ),
                "expectedTimeOnBelt": (
                    flight["expectedTimeOnBelt"]
                    if "expectedTimeOnBelt" in flight.keys()
                    else ""
                ),
                "baggageClaimBelts": (
                    flight["baggageClaim"]["belts"]
                    if "baggageClaim" in flight.keys()
                    else ""
                ),
            }
            arrivals_cleaned.append(processed_flight)
        else:
            # Departures
            processed_flight["departureInfo"] = {
                "gate": (flight["gate"] if "gate" in flight.keys() else ""),
                "expectedTimeBoarding": (
                    flight["expectedTimeBoarding"]
                    if "expectedTimeBoarding" in flight.keys()
                    else ""
                ),
                "expectedTimeGateOpen": (
                    flight["expectedTimeGateOpen"]
                    if "expectedTimeGateOpen" in flight.keys()
                    else ""
                ),
                "expectedTimeGateClosing": (
                    flight["expectedTimeGateClosing"]
                    if "expectedTimeGateClosing" in flight.keys()
                    else ""
                ),
                "actualOffBlockTime": (
                    flight["actualOffBlockTime"]
                    if "actualOffBlockTime" in flight.keys()
                    else ""
                ),
            }
            departures_cleaned.append(processed_flight)

    return arrivals_cleaned, departures_cleaned


def analyse_arrivals(arrivals: list) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to parse arrival data.
    """
    arrival_data = []
    destination_data = {}

    for flight in arrivals:
        arrivalInfo = flight["arrivalInfo"]

        row = {
            "flight_name": flight.get("flight_name"),
            "airline": flight.get("flight_company_prefix"),
            "terminal": flight.get("terminal"),
            "state": flight.get("publicFlightState"),
            "estimatedLandingTime": arrivalInfo.get("estimatedLandingTime"),
            "actualLandingTime": arrivalInfo.get("actualLandingTime"),
            "expectedTimeOnBelt": arrivalInfo.get("expectedTimeOnBelt"),
            "baggageClaimBelts": arrivalInfo.get("baggageClaimBelts"),
        }

        # Drop incomplete rows
        if "" in row.values():
            continue

        arrival_data.append(row)
        arrivalInfo = flight["route"]

        for dest in arrivalInfo["destinations"]:
            destination_data[dest] = (
                destination_data[dest] + 1 if dest in destination_data.keys() else 1
            )
    df_arrival_data = pd.DataFrame(
        arrival_data,
        columns=[
            "flight_name",
            "airline",
            "terminal",
            "state",
            "estimatedLandingTime",
            "actualLandingTime",
            "expectedTimeOnBelt",
            "baggageClaimBelts",
        ],
    )
    df_destination_data = pd.DataFrame([destination_data])

    return df_arrival_data, df_destination_data


def analyse_departures(departures: list) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to parse departure data.
    """
    departure_data = []
    destination_data = {}

    for flight in departures:
        departureInfo = flight["departureInfo"]

        row = {
            "flight_name": flight.get("flight_name"),
            "airline": flight.get("flight_company_prefix"),
            "terminal": flight.get("terminal"),
            "state": flight.get("publicFlightState"),
            "gate": departureInfo.get("gate"),
            "expectedTimeGateOpen": departureInfo.get("expectedTimeGateOpen"),
            "expectedTimeBoarding": departureInfo.get("expectedTimeBoarding"),
            "expectedTimeGateClosing": departureInfo.get("expectedTimeGateClosing"),
            "actualOffBlockTime": departureInfo.get("actualOffBlockTime"),
        }

        # Drop incomplete rows
        if "" in row.values():
            continue

        departure_data.append(row)
        destinationInfo = flight["route"]

        for dest in destinationInfo["destinations"]:
            destination_data[dest] = (
                destination_data[dest] + 1 if dest in destination_data.keys() else 1
            )

    df_departure_data = pd.DataFrame(
        departure_data,
        columns=[
            "flight_name",
            "airline",
            "terminal",
            "state",
            "gate",
            "expectedTimeGateOpen",
            "expectedTimeBoarding",
            "expectedTimeGateClosing",
            "actualOffBlockTime",
        ],
    )
    df_destination_data = pd.DataFrame([destination_data])

    return df_departure_data, df_destination_data


def filter_dataframe(
    df: pd.DataFrame, col_name: str, filter_value: str, group_by_col: str, top_n: int
) -> pd.DataFrame:
    """
    Function that returns the <top_n> entries of column <group_by_col> with the
    most occurrences in the dataframe <df> , when the value of column <col_name> is
    <filter_value>.
    """
    if df.empty:
        logger.warning("Dataframe provided is empty. No analysis provided.")
        return df

    filtered_df = df[df[col_name] == filter_value]

    airline_counts = filtered_df[group_by_col].value_counts().reset_index()
    airline_counts.columns = [group_by_col, "count"]

    top_airlines = airline_counts.nlargest(top_n, "count")

    top_airlines[group_by_col] = top_airlines[group_by_col].map(
        lambda x: fetch_airline(x)["publicName"]
    )
    return top_airlines


def find_most_popular_destinations(df: pd.DataFrame, top_n: int) -> pd.DataFrame:
    """
    Function that returns the <top_n> most popular destination cities in dataframe
    <df>, indicating the city name and the number of flights.
    """
    if df.empty:
        logger.warning("Dataframe provided is empty. No analysis provided.")
        return df

    top_values = df.iloc[0].nlargest(top_n)
    top_columns = top_values.index.tolist()
    top_values = top_values.values.tolist()

    # Create a new DataFrame with columns ["col_name", "value"]
    top_dest_df = pd.DataFrame({"destination": top_columns, "flights": top_values})

    top_dest_df["destination"] = top_dest_df["destination"].map(
        lambda x: fetch_destination(x)["city"]
    )

    return top_dest_df


def find_busiest_facilities(
    df_arrivals: pd.DataFrame, df_departures: pd.DataFrame, top_n: int, window: str
) -> dict:
    """
    A function that returns a dictionary with different information about the
    top <top_n> busiest airport facilities and most popular airlines during the <window>.
    """
    top_baggage_belts_df = pd.DataFrame(columns=["window", "beltID", "count"])
    top_gates_df = pd.DataFrame(columns=["window", "gate", "count"])
    busiest_arr_terminals_df = pd.DataFrame(columns=["window", "terminal", "count"])
    busiest_dep_terminals_df = pd.DataFrame(columns=["window", "terminal", "count"])
    combined_counts_df = pd.DataFrame(columns=["window", "airline", "count"])

    if not df_arrivals.empty:
        top_baggage_belts_df = _find_busy_baggage_belts(df_arrivals, top_n)
        top_baggage_belts_df.loc[:, "window"] = window

        # Select top N busy arrivals' terminals
        terminal_counts = df_arrivals["terminal"].value_counts().reset_index()
        terminal_counts.columns = ["terminal", "count"]
        busiest_arr_terminals_df = terminal_counts.head(top_n).copy()
        busiest_arr_terminals_df.loc[:, "window"] = window

    if not df_departures.empty:
        # Gates
        gate_counts = df_departures["gate"].value_counts()
        top_gates_df = pd.DataFrame(
            list(gate_counts.head(top_n).items()), columns=["gate", "count"]
        )
        top_gates_df.loc[:, "window"] = window

        # Select top N busy departures' terminals
        terminal_counts = df_arrivals["terminal"].value_counts().reset_index()
        terminal_counts.columns = ["terminal", "count"]
        busiest_dep_terminals_df = terminal_counts.head(top_n).copy()
        busiest_dep_terminals_df.loc[:, "window"] = window

    if not df_arrivals.empty or not df_departures.empty:
        combined_counts_df = _find_busy_airlines(df_arrivals, df_departures, top_n)
        combined_counts_df.loc[:, "window"] = window
    return {
        "busy_belts": top_baggage_belts_df,
        "busy_gates": top_gates_df,
        "busiest_arrivals_terminals": busiest_arr_terminals_df,
        "busiest_departure_terminals": busiest_dep_terminals_df,
        "busiest_airlines": combined_counts_df,
    }


def _find_busy_baggage_belts(df, top_n):
    # Baggage belts
    baggage_claim_lists = df["baggageClaimBelts"].tolist()
    all_baggage_claims = [item for sublist in baggage_claim_lists for item in sublist]
    baggage_claim_counts = Counter(all_baggage_claims)
    return pd.DataFrame(
        baggage_claim_counts.most_common(top_n), columns=["beltID", "count"]
    )


def _find_busy_airlines(df_arrivals, df_departures, top_n):
    # Airlines & drop empty lines

    arrivals_counts = df_arrivals[df_arrivals["airline"] != ""][
        "airline"
    ].value_counts()
    departures_counts = df_departures[df_departures["airline"] != ""][
        "airline"
    ].value_counts()

    # Create a DataFrame to aggregate both counts
    combined_counts_df = pd.DataFrame(
        {
            "count": arrivals_counts.add(
                departures_counts, fill_value=0
            )  # Add counts, fill NaN with 0
        }
    )
    combined_counts_df = combined_counts_df.sort_values(by="count", ascending=False)
    combined_counts_df = combined_counts_df.head(top_n)
    combined_counts_df["airline"] = combined_counts_df.index.map(
        lambda x: fetch_airline(x)["publicName"]
    )
    return combined_counts_df.reset_index(drop=True)
